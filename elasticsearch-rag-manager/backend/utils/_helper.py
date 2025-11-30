import json
import aiofiles
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import config as cfg


# def read_json_file(file_path):
#     with open(file_path, "r") as f:
#         return json.load(f)
    

async def read_json_file(file_path):
    async with aiofiles.open(file_path, "r") as f:
        data = await f.read()
    return json.loads(data)

    
def get_query_for_new_id():
    query = {
    "size": 0,  # No need to return documents
    "aggs": {
        "max_id": {
            "max": {
                "field": "id"
                }
            }
        }
    }   
    return query


def transform_dict_n_str(_input, dict_2_str=True):
    if dict_2_str:
        _output = json.dumps(_input, ensure_ascii=False)
    else: # str 2 dict
        _output = json.loads(_input)
    return _output


def get_metadata_index_name():
    return



def setup_logger():
    # Create the log directory if it does not exist
    os.makedirs(cfg.path_logs, exist_ok=True)
    
    app_logger = logging.getLogger("myapp")
    app_logger.setLevel(logging.DEBUG)

    # Check if handlers are already added to avoid duplication
    if not app_logger.handlers:
        # Create a handler for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        app_logger.addHandler(console_handler)

        # Create a single TimedRotatingFileHandler for all log levels
        log_file_handler = TimedRotatingFileHandler(
            os.path.join(cfg.path_logs, "backend_log"),
            when="midnight",
            interval=1,
            backupCount=7  # Keep logs for the last 7 days
        )
        log_file_handler.suffix = "%Y-%m-%d"
        log_file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
        log_file_handler.setFormatter(file_format)
        app_logger.addHandler(log_file_handler)

    return app_logger


def propagate_uvicorn_logger():
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False