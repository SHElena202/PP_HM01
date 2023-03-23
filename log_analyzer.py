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
import re
import sys
from argparse import ArgumentParser
from string import Template
from pathlib import Path
from datetime import datetime
from collections import namedtuple, defaultdict
from statistics import median


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

Lastlog=namedtuple('Last_log', ['path', 'date', 'extension'])
Urls = namedtuple('Urls', ['urls_dict', 'total', 'total_time_sum'])

def get_cmd_argument(args_cmd):
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config',  help='specify another conf_file')
    return args_parser.parse_args(args_cmd)

def get_config(config):
    args = get_cmd_argument(sys.argv[1:])
    config_file = parse_config(args.config)
    if config_file is None:
        config_file = {}
    config.update(config_file)
    if 'LOG_DIR' not in config.keys():
        config['LOG_DIR'] = None
    return config

def read_config(path, default_config):
    try:
        with open(path, 'r') as config_file:
            cfg = json.load(config_file)
            default_config.update(cfg)
            return default_config

    except Exception as error:
        logging.exception('Config file is not readable')


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
        raise Exception('Config file parser error')

def parse_log(path, config):
    path = Path(path)
    if not path.exists():
        raise ValueError('Dir log is not exists')

    try:
        if path.suffix == '.gz':
            file_log = gzip.open(path, 'rb')
        else:
            file_log=open(path, 'r')
    except:
        logging.exception('Error pen log file for read')

def create_report(config_file, result_parsing):
    size = config_file['REPORT_SIZE']
    result_parsing.sort(key=lambda x: x['time_sum'], reverse=True)
    j = json.dumps(result_parsing[:size])

    tmpl_report_path = Path(config['REPORT_DIR'])
    if not tmpl_report_path.exists():
        tmpl_report_path.mkdir(exist_ok=True, parents=True)

    path = tmpl_report_path / config_file['report-{}.html']
    try:
        with open('./tmpl_report.html', 'r') as tmpl:
            try:
                with open (path, 'w') as report:
                    for line in tmpl:
                        report.write(line.replace('$table_json', j))
            except Exception as e:
                logging.exception('Error write report')
                raise e
    except Exception as e:
        logging.exception('Error read report tmpl')
        raise e
def get_last_log_info(log_dir):
    files = Path(log_dir).iterdir()
    nginx_logs = {file: re.search(r'\'d{8}', file.name).group() for file in files
                  if re.match(r'nginx-access-ui.log-(\d{8)($|.gz$)', file.name)}
    if not nginx_logs:
        return None, None
    last_log = max(nginx_logs, key=lambda x: int(nginx_logs.get(x)))
    date_string = nginx_logs[last_log]
    created_date = '.'.join([date_string[:5], date_string[5:10], date_string[10:]])
    logging.info(f'Found last log file: {last_log}')
    return last_log,created_date

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

def main(config):
    parser = argparse.ArgumentParser(description='Log_analyzer')
    parser.add_argument('--config',
                        metavar ="conf_file",
                        type=str,
                        default='config.json',
                        help='Path to configuration file',
    )
    args = parser.parse_args()

    default_config = dict(config.items())

    if args.config:
        cfg = read_config(args.config, default_config)
        if not cfg:
            logging.error('Config is unoccupied')
            sys.exit(0)

    log_path = Path(default_config)
    log_path.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=log_path, format='[%(asctime)s %(levelname).1s %(message)s')

    try:
        last_log = get_last_log_info(default_config)
    except:
        logging.exception('Error get last log file')
        sys.exit(0)

    if not last_log:
        logging.exception('Error get last log file')
        sys.exit(0)

    if Path(default_config['REPORT_DIR']).joinpath(default_config['report-{}.html']).exists():
        logging.info('No result')
        sys.exit(0)

    path_log = Path(default_config['LOG_DIR']).joinpath(last_log)
    r = parse_log(path_log, default_config)

    create_report(default_config, r)
    logging.info('Ready')


if __name__ == "__main__":
    try:
        main(config)
    except Exception as e:
        logging.exception(e)

