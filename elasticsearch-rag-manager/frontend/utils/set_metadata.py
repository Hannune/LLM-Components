"""
This file will provide the metadata for the RAG page.
The metadata will be used for adding data to elastic search, creating new indexes, and embedding data.

So the metadata will be in 2 different forms:
1. Original data
2. Vectors and original data

"""
mappings = {
    "metadata": {
        "index_name": "",
        "user": "",
        "description": "",
        "Index_type": "",
        "creation_date": "",
        "embedding_models": "",
        "latest_update": "",
        "id": "",
        "number_of_data": "",
        "matching_original_index": "",
        "index_type_id": "",
        "full_text_preprocessing": "",
        "generated_full_vector_index_info": "",
        "generated_chunked_pairs_index_info": ""
    },
    "relations": {
        "similarity": "",
        "full_vector_index": "",
        "full_text_index": "",
        "similarity_shape": "",
        "recent_update_date": "",
        "similarity_type": ""
    },
    "full_text": {
        "title": "",
        "pages": "",
        "author": "",
        "published_date": "",
        "added_date": "",
        "characters": "",
        "description": "",
        "series_id": "",
        "url": "",
        "source_type": "",
        "text": "",
        "file_name": "",
        "id": ""
    },
    "full_vector": {
        "vector": "",
        "original_title": "",
        "original_id": "",
        "vector_shape": "",
        "added_date": ""
    },
    "chunked_pair": {
        "chunked_vectors": "",
        "chunked_texts": "",
        "original_title": "",
        "original_id": "",
        "vector_shape": "",
        "added_date": "",
        "chunk_size": "",
        "overlaps": "",
        "separator": ""
    }
}



def get_mapping_keys(_type:str):
    if _type == "full_text":
        metadata = {
            "title": "",
            "pages": "",
            "author": "",
            "published_date": "",
            "added_date": "",
            "characters": "",
            "description": "",
            "series_id": "",
            "url": "",
            "source_type": "",
            "text": "",
            "file_name": "",
            "id": ""
        }
    elif _type == "full_vector":
        metadata = {
            "vector": "",
            "original_title": "",
            "original_id": "",
            "vector_shape": "",
            "added_date": ""
        }
    elif _type == "chunked_pair":
        metadata = {
            "chunked_vectors": "",
            "chunked_texts": "",
            "original_title": "",
            "original_id": "",
            "vector_shape": "",
            "added_date": "",
            "chunk_size": "",
            "overlaps": "",
            "separator": ""
        }
    elif _type == "metadata":
        metadata = {
            "index_name": "",
            "user": "",
            "description": "",
            "Index_type": "",
            "creation_date": "",
            "embedding_models": "",
            "latest_update": "",
            "id": "",
            "number_of_data": "",
            "matching_original_index": "",
            "index_type_id": "",
            "full_text_preprocessing": "",
            "generated_full_vector_index_info": "",
            "generated_chunked_pairs_index_info": ""
        }
    elif _type == "relations":
        metadata = {
            "similarity": "",
            "full_vector_index": "",
            "full_text_index": "",
            "similarity_shape": "",
            "recent_update_date": "",
            "similarity_type": ""
        }

    
    return metadata