import requests
import os
from dotenv import load_dotenv
import json
import config as cfg
from utils.helper import handle_response

# load_dotenv()
load_dotenv(cfg.path_dotenv)

# TODO: check if the response is valid
class _db_api:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_IP_PORT")


    def get_properties(self, index_type="all"):
        url = self.base_url + "/get/properties/"
        params = {"index_type": index_type}
        res = requests.get(url, params=params)
        return handle_response(res)


    def get_models_list(self):
        url = self.base_url + "/get/models-list/"
        res = requests.get(url)
        return handle_response(res)


    def get_all_data_in_index_with_fields(self, index_name, fields):
        url = self.base_url + "/get/all-data-in-index-with-fields/"
        _json = {"target_index": index_name, "target_fields": fields}
        res = requests.get(url, json=_json)
        return handle_response(res)


    def get_job_manager_status(self):
        url = self.base_url + "/get/job-manager-status/"
        res = requests.get(url)
        return handle_response(res)


    def get_all_index(self):
        url = self.base_url + "/get/all-index/"
        res = requests.get(url)
        return handle_response(res)


    def post_add_index(self, index_type, index_name, properties):
        _json = {
            "index_type": index_type, # full_text, full_vector, chunked_pairs
            "index_name": index_name, 
            "metadata_properties": properties # properties for metadata index
            }

        # add new index
        url = self.base_url + "/post/add-index/"

        # add new index
        res = requests.post(url, json=_json)
        if res.status_code != 200:
            return res.json()

        # if adding new index success, add data to metadata index
        url = self.base_url + "/post/add-data-to_metadata-index/"
        res = requests.post(url, json=_json)

        if res.status_code != 200:
            results = {"add-index": res.json()}
            # if adding data failed, remove the index
            res = self.delete_remove_index(index_name)
            results["remove-index"] = res.json()           
            return results

        return handle_response(res)
    

    def post_add_data(self, jobs):
        """
        jobs: List[job]
        job = {
            "settings":{
                "target_index_type": "full_text",
                "index_name_full_text": st.session_state["selected_index"],
                "index_name_full_vector": None,
                "index_name_chunked_pairs": None,
                "properties": properties, 
                "embedding_model": None,
                "metadata_index_modify_id": st.session_state["selected_index_id"],
                "full_text_index_modify_id": None,
            },
            "text_file": text_file
        }
        """
        url = self.base_url + "/post/add-jobs"
        files = []
        cnt = 0
        for job in jobs:
            files.append(("settings", (None, json.dumps(job["settings"]), "application/json")))
            cnt += 1
            if job["text_file"] is not None:
                files.append(("text_files", (job["text_file"].name, job["text_file"], "application/octet-stream")))
                cnt -= 1        

        if cnt != 0 and job["text_file"] is not None:
            return {"error": "number of text_files and settings are not equal"}
                
        res = requests.post(url, files=files)
        return handle_response(res)


    def delete_remove_index(self, index_name):
        url = self.base_url + "/delete/remove-index/"
        params = {"index_name": index_name}

        res = requests.delete(url, params=params)
        return handle_response(res)


    def reset_es(self):
        url = self.base_url + "/post/reset-es/"
        res = requests.post(url)
        return handle_response(res)


    