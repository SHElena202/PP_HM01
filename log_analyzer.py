#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '  
#                     '$request_time';
import gzip
import configparser
import argparse
import logging
import json

from string import Template
from pathlib import Path


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def init_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", metavar='<path>', dest='config', help="path to config file", default='settings.ini')
    conf_file = parser.parse_args().config

    if not Path(conf_file).exists():
        raise Exception("Config file not found")

    return conf_file

def parse_config(conf_file):
    try:
        cp=configparser.ConfigParser()
        cp.read(conf_file)
        cp_section = cp['config']
        report_size = int(cp_section.get('REPORT_SIZE', config.get('REPORT_SIZE')))
        report_dir = cp_section.get('REPORT_DIR', config.get('REPORT_DIR'))
        log_dir = cp_section.get('LOG_DIR', config.get('LOG_DIR'))
        return report_size, report_dir, log_dir
    except:
        raise Exception("Config file parser error")

def make_report(data, report):
    template =Template(Path('report.html').read_text(encoding='utf-8'))
    content = template.safe_substitute(table_json=json.dumps(data))
    Path(report).write_text(content, encoding='utf-8')
    logging.info('Report generated success')

def render_report(data, file_name, template_dir):
    with open(template_dir, encoding='utf-8') as temp:
        template = Template(temp.read())
    with open(file_name, "w", encoding='utf-8') as fh:
        report = template.safe_substitute(teble_json=data)
        fh.write(report)

def read_file(file_name, extension):
    file = gzip.open(file_name, 'rb') if extension == 'gz' else open(file_name, 'rb')
    for row in file:
        yield row.decode()


def main():
    parser = argparse.ArgumentParser(description='Log_analyzer')
    parser.add_argument('--conf',
                        metavar="conf_file",
                        type=str,
                        default='config.json',
                        help='Path to configuration file',
                        required = False,
    )
    args = parser.parse_args()


if __name__ == "__main__":
    main()
