import json
import logging
import argparse
import os
import time

import math
import asyncio
import websockets
from core.models.config import Config
from core.stages.steps_stage import StepsStage
from core.stages.summary_stage import SummaryStage
from core.utils.file_util import get_project_related_file_path
import yaml

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: green + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s" + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

parser = argparse.ArgumentParser(description='')
parser.add_argument('project_folder', help='Path to project folder')
parser.add_argument('--config_file_name', default='config.yml', help='Name of the config file')
args = parser.parse_args()
loop = asyncio.get_event_loop()

def main():
    config_file_path = f"{args.project_folder}/{args.config_file_name}"
    print(f"load config file: {config_file_path} ...")
    config_data = None
    # load the config file
    try:
        with open(config_file_path, 'r') as f:
            config_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error: could not load config file {config_file_path}: {e}")
        exit(1)

    config = Config.from_json(config_data, project_folder=args.project_folder)

    stages = [
        StepsStage(),
        SummaryStage()
    ]

    for stage in stages:
        stage.run(config)


if __name__ == '__main__':
    main()