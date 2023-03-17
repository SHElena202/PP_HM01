import shutil
import pytest
from random import randint
import log_analyzer
from log_analyzer import *


def rng_num(lenght):
    return "".join([str(randint(1,9)) for _ in range(lenght)])

@pytest.fixture
def make_mixed_config():
    test_dir = 'test_dir'
    Path(test_dir).mkdir()
    config = Path(test_dir).joinpath('config.txt')
    data = {'REPORT_SIZE': rng_num(10)}
    Path(config).write_text(f"[config]\n"
                            f"REPORT_SIZE = {data['REPORT_SIZE']}\n"
                            )
    yield config.resolve(), data
    shutil.rmtree(test_dir)

def test_parsing_mixed_config(make_mixed_config):
    config, data = make_mixed_config
    report_size, report_dir, log_dir = log_analyzer.parse_config(config)
    assert str(report_size) == data['REPORT_SIZE']
    assert report_dir == log_analyzer.config['REPORT_DIR']
    assert log_dir == log_analyzer.config['LOG_DIR']

