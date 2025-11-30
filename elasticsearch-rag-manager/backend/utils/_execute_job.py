from datetime import datetime
from utils._helper import get_query_for_new_id, transform_dict_n_str
import config as cfg
import numpy as np
import time


class execute:
    def __init__(self, es, model, logger, naive_text_extraction, naive_sentence_chunking, naive_word_chunking, semantic_chunking):
        self.es = es
        self.model = model
        self.naive_text_extraction = naive_text_extraction
        self.naive_sentence_chunking = naive_sentence_chunking
        self.naive_word_chunking = naive_word_chunking
        self.semantic_chunking = semantic_chunking
        self.info = None
        self.output = None
        self.current_step = "idle"
        self.logger = logger
        """
        self.info: dict
            "target_index_type",
            "index_name_full_text",
            "index_name_full_vector",
            "index_name_chunked_pairs",
            "properties", 
            "text_file",
            "embedding_model",
            "metadata_index_modify_id",
            "full_text_index_modify_id"
        """


    def modify_data(self, modify_index_name, data_added_index_name=None, data_added_index_id=None, data_added_data_id=None):
        self.current_step = "modify_data"

        """
        data is added to any index, update metadata index
            todo: modify 'latest_update' and 'number_of_data' fields in metadata_<data_added_index_type> index
                fields -> {"latest_update": datetime.now().isoformat(), "number_of_data": number_of_data + 1}
            inputs: data_added_index_type, data_added_index_name, data_added_index_name
        """

        if modify_index_name.startswith("metadata"):
            # modify metadata index
            modify_index_type = "metadata"
            target_data_id = self.info["metadata_index_modify_id"]
            fields = ["latest_update", "number_of_data"]
            self.es.post_modify_data(
                modify_index_type, 
                modify_index_name, 
                target_data_id, 
                fields
            )
        

    def extract_text(self, text_file):
        self.current_step = "extract_text"

        self.output = self.naive_text_extraction.start(
            file_instance = text_file, 
            doc_title = self.info["properties"]["title"], 
            doc_type = self.info["properties"]["source_type"]
            )
        self.output = transform_dict_n_str(self.output, dict_2_str=True)
        

    def modify_properties(self):
        self.current_step = "modify_properties"

        # modify(add) properties which imcomplete sent from frontend 
        self.info["properties"]["added_date"] = datetime.now().isoformat()
        
        if self.info["target_index_type"] == "full_text":
            target_index = self.info["index_name_full_text"]

        elif self.info["target_index_type"] == "full_vector":
            target_index = self.info["index_name_full_vector"]
            self.info["properties"]["vector"] = self.output
            
        elif self.info["target_index_type"] == "chunked_pairs":
            target_index = self.info["index_name_chunked_pairs"]
            self.info["properties"]["chunked_text_vector_pairs"] = self.output

        # # id is no longer added
        # _id = self.es.get_id_sync(target_index)
        # self.info["properties"]["id"] = _id
        

    def add_to_es(self):
        self.current_step = "add_to_es"
        # if target index type is full_vector or chunked_pairs, data in full_text index should be modified
        # when data is being added latest update, number of data field should be updated to metadata_<target_index_type> index

        # target_index_name, data_added_index_name, data_added_index_id, data_added_data_id

        if self.info["target_index_type"] == "full_text":
            self.info["properties"]["text"] = self.output
            self.es.post_add_data(index_name=self.info["index_name_full_text"], properties=self.info["properties"]) 

        elif self.info["target_index_type"] == "full_vector":
            self.info["properties"]["vector"] = self.output
            res = self.es.post_add_data(index_name=self.info["index_name_full_vector"], properties=self.info["properties"])
            self.info["properties"]["id"] = res["response"]["_id"]

        elif self.info["target_index_type"] == "chunked_pairs":
            self.info["properties"]["chunked_text_vector_pairs"] = self.output
            res = self.es.post_add_data(index_name=self.info["index_name_chunked_pairs"], properties=self.info["properties"])
            self.info["properties"]["id"] = res["response"]["_id"]


        try:
            self.modify_data(f'metadata_{self.info["target_index_type"]}', data_added_index_name=self.info["index_name_full_vector"])
        except Exception as e:
            self.logger.exception(f"Error in add_to_es() in metadata: {e}")
        

    def retrieve_text(self):
        self.current_step = "retrieve_text"

        # option 1
        retrieved_full_text_in_str = self.es.get_data_match_id(
            index_name = self.info["properties"]["original_full_text_index_name"],
            _id = self.info["properties"]["original_full_text_data_id"],
            target_fields = ["text"]        
        )

        """
        # option 2
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"title": self.info["properties"]["original_full_text_data_title"]}},
                        {"match": {"id": self.info["properties"]["original_full_text_data_id"]}}
                    ]
                }
            },
            "_source": ["text"]  # Only retrieve field2 from the matches
        }
        retrieved_full_text_in_str = self.es.retrieve_full_text(
            index_name = self.info["index_name_full_text"],
            query = query
        )        
        """

        self.output = retrieved_full_text_in_str["text"]
        self.output = transform_dict_n_str(self.output, dict_2_str=False)


    def embed_text(self):
        
        # if target index type is chunked_pairs, output is list of dict(text, vector)
        # if target index type is full_vector, output is np.array
        
        self.current_step = "embed_text"

        # get settings for embedding
        embedding_model = self.info["embedding_model"]
        batch_size = cfg.batch_size_base
        if embedding_model in cfg.embedding_models_info:
            if "recommended_batch_size" in cfg.embedding_models_info[embedding_model]:
                batch_size = cfg.embedding_models_info[embedding_model]["recommended_batch_size"]
        
        # embed text
        output = []
        for i in range(0, len(self.output), batch_size):
            batch_text = self.output[i:i+batch_size]
            batch_vector = self.model.embedding(embedding_model, batch_text)

            if self.info["target_index_type"] == "full_vector":
                output.extend(batch_vector)
            elif self.info["target_index_type"] == "chunked_pairs":
                for text, vector in zip(batch_text, batch_vector):
                    _pair = {}
                    _pair["text"] = text
                    _pair["vector"] = vector
                    output.append(_pair)
            time.sleep(0.5)

        # if target index type is full_vector, perform pooling
        if self.info["target_index_type"] == "full_vector":
            method = "mean"
            if method == "mean":
                output = np.mean(output, axis=0)
            elif method == "max":
                output = np.max(output, axis=0)

        self.output = output


    def chunk_text(self):
        self.current_step = "chunk_text"

        if self.info["target_index_type"] == "full_vector":
            self.naive_sentence_chunking.chunk_size = cfg.embedding_models_info[self.info["embedding_model"]]["sequence_length"]//4
            self.naive_sentence_chunking.overlap = cfg.chunking_methods["naive_sentence_chunking"]["overlap"]
            self.output = self.naive_sentence_chunking.start(self.output)

        elif self.info["target_index_type"] == "chunked_pairs":
            self.semantic_chunking.set_instance_variable(self.info)
            self.output = self.semantic_chunking.start(self.output)
        # self.output is list chunked texts
        

    def add_full_text(self, info, text_file):

        # extract text
        self.extract_text(text_file)

        # modify properties
        self.modify_properties()                         

        # add to es
        self.add_to_es()



    def add_full_vector(self, info):

        # retrieve text
        self.retrieve_text()

        # chunk text
        self.chunk_text()

        # embed text
        self.embed_text()

        # modify properties
        self.modify_properties()

        # add to es
        self.add_to_es()
        

    def add_chunked_pairs(self, info):

        # retrieve text
        self.retrieve_text()

        # chunk text
        self.chunk_text()

        # embed text
        self.embed_text()

        # modify properties
        self.modify_properties()

        # add to es
        self.add_to_es()


    def start(self, info, job_type, text_file=None):
        self.info = info
            
        if job_type == "full_text":
            self.add_full_text(info, text_file)
        elif job_type == "full_vector":
            self.add_full_vector(info)
        elif job_type == "chunked_pairs":
            self.add_chunked_pairs(info)

        # reset
        self.info = None
        self.output = None
        self.current_step = "idle"

        return True