"""
All the funcitons using elastic search will be defined here
get/post
"""

import os
from dotenv import load_dotenv
import config as cfg
from elasticsearch import AsyncElasticsearch, Elasticsearch
import asyncio
from datetime import datetime
from utils._helper import read_json_file

# from concurrent.futures import ThreadPoolExecutor
# from functools import partial


# load_dotenv(dotenv_path=cfg.path_dotenv)
load_dotenv(cfg.path_dotenv)



class _ElasticSearch:
    def __init__(self, logger):
        self.client, self.client_sync = self.get_client()
        self.logger = logger
        # self.loop = asyncio.get_event_loop()
        # self.executor = ThreadPoolExecutor(max_workers=cfg.max_thread_workers)


    def get_client(self):
        ip = os.getenv("ELASTIC_CLOUD_IP")
        port = os.getenv("ELASTIC_CLOUD_PORT")
        client = AsyncElasticsearch(hosts=f"http://{ip}:{port}", basic_auth=("username", "password"))
        client_sync = Elasticsearch(hosts=f"http://{ip}:{port}", basic_auth=("username", "password"))
        return client, client_sync


    async def get_data_match_all(self, index_name, query):
        res = await self.client.search(index=index_name, body=query, size=cfg.max_documents_to_retrieve_from_es)
        return res


    async def remove_index(self, index_name):
        if bool(await self.client.indices.exists(index=index_name)):
            res = await self.client.indices.delete(index=index_name)
        else:
            res = {"status": "skipped", "message": "index does not exist"}
        return res
            


    
    def get_data_match_all_sync(self, index_name, query, _id=None, target_fields=None): ##### might be deprecated
        if _id is None:
            if target_fields is not None:
                res = self.client_sync.search(index=index_name, body=query, _source=target_fields, size=cfg.max_documents_to_retrieve_from_es)
            res = self.client_sync.search(index=index_name, body=query, size=cfg.max_documents_to_retrieve_from_es)
            return res
        
        return res

    
    def get_data_match_id(self, index_name, _id, target_fields):
        res = self.client_sync.get(index=index_name, id=_id, _source=target_fields)
        res = res["_source"]
        return res
            

    def retrieve_full_text(self, index_name, query):
        res = self.client_sync.search(index=index_name, body=query, size=cfg.max_documents_to_retrieve_from_es)
        return res


    async def post_add_index(self, index_name, properties):
        """
        Add new index to the elastic search
        """
        if index_name == "index_name":
            self.logger.exception(f"in _ElasticSearch.post_add_index: index_name is not set") 
        body = {"mappings": {"properties": properties}}
        try:
            await self.client.indices.create(index=index_name, body=body)
        except Exception as e:
            return {"status": "fail", "message": str(e)}
            raise
        return {"status": "success", "message": "index created"}

        

    def post_add_data(self, index_name, properties: dict):

        try:
            response = self.client_sync.index(index=index_name, document=properties)
        except Exception as e:
            self.logger.exception(f"Error in post_add_data: {str(e)}")
            raise

        return {"status": "success", "response": response}


    def post_modify_data(self, 
                        modify_index_type, 
                        modify_index_name, 
                        target_data_id, 
                        fields, 
                        data_added_index_type=None,
                        data_added_index_name=None,
                        data_added_index_id=None,
                        data_added_data_id=None
                        ):

        """
        This modification will take place when the data is added to index

        data is added to any index, update metadata index
            todo: modify 'latest_update' and 'number_of_data' fields in metadata_<data_added_index_type> index
            inputs: data_added_index_type, index_name, fields, data_added_index_name
        
        """

        # retrieve the field to be modified
        fields = self.client_sync.get(index=modify_index_name, id=target_data_id, _source=fields)["_source"]
        
        # modify the field
        if modify_index_type == "metadata":
            fields["latest_update"] = datetime.now().isoformat()
            fields["number_of_data"] += 1
        elif modify_index_type == "full_text":
            fields[f"child_{data_added_index_type}_indexes"].append(
                                        {
                                            f"index_name_{data_added_index_type}": data_added_index_name,
                                            f"index_id_{data_added_index_type}": data_added_index_id,
                                            f"data_id_{data_added_index_type}": data_added_data_id
                                        }
                                    )

        # update the field
        self.client_sync.update(index=modify_index_name, id=target_data_id, body={"doc": fields})


    async def reset_es(self):
        # get all index
        indices = await self.client.cat.indices(format="json")
        indices = [index["index"] for index in indices]

        results = {}
        for index in indices:
            if index[0] == ".":
                continue
            res = await self.remove_index(index)
            results.update({index: res})

        PROPERTIES_DIR = os.getenv("PROPERTIES_DIR")
        properties_all = await read_json_file(PROPERTIES_DIR)

        metadata_type_list = [
            "INDEX_NAME_METADATA_FULL_TEXT", 
            "INDEX_NAME_METADATA_FULL_VECTOR", 
            "INDEX_NAME_METADATA_CHUNKED_PAIRS"
            ]
        for metadata_type in metadata_type_list:
            index_name_metadata = os.getenv(metadata_type)
            properties = properties_all[index_name_metadata]
            res = await self.post_add_index(index_name_metadata, properties)
            results.update({index_name_metadata: res})
        
        return results




