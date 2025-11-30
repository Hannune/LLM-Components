"""
Since this backends purpose is for RAG with documents
each documents added to index in elasticsearch will be called data instead of documents
"""

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
import uvicorn
import asyncio
from asyncio import Queue
import io
import json

import config as cfg
from utils._elastic_search import _ElasticSearch
from utils._job_management import _JobManagement
from utils._get_query import GetQuery
from utils._models_api import _fastchat_openai_api
from utils._helper import read_json_file, setup_logger, propagate_uvicorn_logger

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

import os
from dotenv import load_dotenv

load_dotenv(cfg.path_dotenv)
logger = setup_logger()
propagate_uvicorn_logger()

es = _ElasticSearch(logger)
app = FastAPI()
model = _fastchat_openai_api(logger)
job_manager = _JobManagement(es, model, logger)
fastchat = _fastchat_openai_api(logger)
queries = GetQuery()



class post_add_index_param(BaseModel):
    index_type: str
    index_name: str
    metadata_properties: dict


class get_search_es_query_param(BaseModel):
    index_name: str
    query: dict


class get_data_param(BaseModel):
    target_index: str
    target_fields: List[str]

    
class post_add_jobs_param(BaseModel):
    jobs: List[dict]


@app.get("/get/job-manager-status/")
async def get_job_manager_status():    
    logger.info(f"request for get_job_manager_status()")
    status = await job_manager.get_status_summary()
    logger.info(f"request for get_job_manager_status() success")
    return status


@app.get("/get/properties/")
async def properties(index_type:str):
    """
    index_type: keyword, [full_text, full_vector, chunked_pairs]
    Get keys of the index type
    """
    logger.info(f"request for properties() of {index_type} index")
    # This may be replaced with other method
    PROPERTIES_DIR = os.getenv("PROPERTIES_DIR")
    properties = await read_json_file(PROPERTIES_DIR)
    if properties == None:
        logger.error(f"request for properties() of {index_type} index failed")
        return None

    logger.info(f"request for properties() of {index_type} index success")
    return properties


@app.get("/get/models-list/")
async def get_models_list(model_type:str="embedding"):
    """
    model_type: keyword, [llm, embedding]
    Get list of models from Fastchat api(chatGPT)
    """
    logger.info(f"request for get_models_list() of model")
    models_list = await fastchat.get_models_list()
    models_list = {model["id"]:{} for model in models_list["data"]}
    for model in models_list.keys():
        if "embedding" in model:
            info = cfg.embedding_models_info[model]
            models_list[model] = info
    logger.info(f"request for get_models_list() of model success, {len(models_list)} models found")
    return models_list


@app.get("/get/all-index/")
async def get_all_index():
    logger.info(f"request for get_all_index()")
    index_name_list = await es.client.cat.indices(format="json")
    index_name_list = [index["index"] for index in index_name_list]
    logger.info(f"request for get_all_index() success, {len(index_name_list)} indices found")
    return index_name_list


@app.get('/get/all-data-in-index-with-fields/')
async def get_all_data_in_index_with_fields(info:get_data_param):

    """
    Get data from selected index with certain fields of properties with query

    cases
        1. Get id for newly created data from selected index
            input: target_index="<target index name>", target_fields=["id"]
            return: integer
        2. Get index name list for specified index type from metadata index(get index name list)
            input: target_index="metadata_<index_type>", target_fields=["index_name"]
            return: dict[index_type: list(index_names)]
                [{"index_name":index_name1}, {"index_name":index_name2}, ...]
        3. Get title of data from selected index(get data title list)
            input: target_index="<selected index name>", target_fields=["title"]
            return: dict[index_name: list(titles)]
                [{"title":title1}, {"title":title2}, ...]
        4. Get embedding models from selected index(get rule list)
            input: target_index="metadata_<index_type>", target_fields=["index_name", field1, field2, ...]
            return: dict[index_name: list(embedding_model, vector size, ...)]
                [{"index_name":index_name1, "field1":field1, "field2":field2, ...}, {"index_name":index_name2, "field1":field1, "field2":field2, ...}, ...]
    input params
        target_index: str
        target_fields: list
    """
    logger.info(f"request for get_all_data_in_index_with_fields()")
    if "id" in info.target_fields:
        info.target_fields.remove("id")
    query = {
            "_source": info.target_fields,  # Specify the fields you want to retrieve
            "query": {
                "match_all": {}  # Use a match_all query to retrieve all documents; customize as needed
            }
        }

    try:
        res = await es.get_data_match_all(info.target_index, query)
    except Exception as e:
        logger.exception(f"request for get_all_data_in_index_with_fields() failed: {str(e)}")
        # return {"status": "failed", "message": str(e)}

    hits = res["hits"]["hits"]
    data_list = {}
    for hit in hits:
        _id = hit["_id"]
        _data = hit["_source"]
        _data.update({"id":_id})
        data_list.update({hit["_source"][info.target_fields[0]]:_data})
    
    logger.info(f"request for get_all_data_in_index_with_fields() success")

    return data_list


@app.post("/post/add-index/")
async def add_index(info:post_add_index_param):
    """
    index_type: keyword, [metadata, full_text, full_vector, chunked_pairs]
    index_name:str
    metadata_properties: dict of str, {names: str, embedding_models: str, ...}
    
    Adding data to metadata index should also be executed after creating new index
    """
    logger.info(f"request for add_index()")
    # Get properties for new index
    PROPERTIES_DIR = os.getenv("PROPERTIES_DIR")
    properties_all = await read_json_file(PROPERTIES_DIR)
    properties_index_type = properties_all[info.index_type]

    if info.index_type == "full_vector":
        properties_index_type["vector"]["dims"] = info.metadata_properties["vector_size"]
    elif info.index_type == "chunked_pairs":
        properties_index_type["chunked_text_vector_pairs"]["properties"]["vector"]["dims"] = info.metadata_properties["vector_size"]

    # Add new index
    result = await es.post_add_index(info.index_name, properties_index_type)
    if result["status"] != "success":
        logger.info(f"add new index failed: {result}")
        return {"status": "failed", "message": result["message"]}
    else:
        logger.info(f"add new index success: {result}")
    return result
    

@app.post("/post/add-index-metadata/")
async def add_index_metadata():
    logger.info(f"request for add_index_metadata()")
    metadata_type_list = [
        "INDEX_NAME_METADATA_FULL_TEXT", 
        "INDEX_NAME_METADATA_FULL_VECTOR", 
        "INDEX_NAME_METADATA_CHUNKED_PAIRS"
        ]
    PROPERTIES_DIR = os.getenv("PROPERTIES_DIR")
    properties_all = await read_json_file(PROPERTIES_DIR)
    results = {}
    for metadata_type in metadata_type_list:
        index_name = os.getenv(metadata_type)
        properties = properties_all[index_name]

        result = await es.post_add_index(index_name, properties)
        results.update({index_name:result})
    logger.info(f"request for add_index_metadata() success")
    return results


@app.post("/post/add-data-to_metadata-index/")
async def add_data_to_metadata_index(info:post_add_index_param):
    """
    currently this function is used when adding new data to one of 3 types of meadata index
    for adding data to other index, `post_add_jobs` function will be used
    """
    logger.info(f"request for add_data_to_metadata_index()")
    # Add new data to metadata index
    result = es.post_add_data(f"metadata_{info.index_type}", info.metadata_properties)
    if result["status"] != "success":
        logger.info(f"add new data to metadata {info.index_type} index failed: {result}")
        # Remove newly created index because metadata index creation failed
        return HTTPException(status_code=400, detail=result["error"])
    logger.info(f"add new data to metadata {info.index_type} index success")
    return result


@app.post("/post/add-jobs/")
async def add_jobs(settings: list[str], text_files: list[UploadFile]=None):
    logger.info(f"request for add_jobs()")
    jobs = []
    if text_files == []:
        text_files = [None for _ in settings]

    for setting, text_file in zip(settings, text_files):
        job = {}
        job["settings"] = json.loads(setting)
        if text_file != None:
            text_file = await text_file.read()
            text_file = io.BytesIO(text_file)
        job["text_file"] = text_file
        jobs.append(job)

    logger.info(f"Received {len(jobs)} jobs")

    previous_queue_size = len(job_manager.queue)
    job_manager.add_new_jobs(jobs)

    logger.info(f"All the jobs has been added")

    if job_manager.status == "idle":
        job_manager.status = "busy"
        asyncio.create_task(job_manager.start_jobs())

    logger.info(f"request for add_jobs() success")
    return {"status": "success", "queue_size": f"{previous_queue_size} -> {len(job_manager.queue)}"}


@app.delete("/delete/remove-index/")
async def delete_remove_index(index_name:str):
    """
    index_name_list: list
    """
    logger.info(f"request for delete_remove_index()")
    result = await es.remove_index(index_name)
    logger.info(f"request for delete_remove_index() success")
    return result


@app.post("/post/reset-es/")
async def reset_es():    
    logger.info(f"request for reset_es()")
    try:
        results = await es.reset_es()
        logger.info(f"request for reset_es() success")
    except Exception as e:
        logger.exception(f"request for reset_es() failed: {str(e)}")
        return {"status": "failed", "message": str(e)}
    return result



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, timeout_keep_alive=30)
    