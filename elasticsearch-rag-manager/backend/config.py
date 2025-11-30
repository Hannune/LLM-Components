max_num_docs_for_embedding = 10
max_num_docs_for_upload = 10
path_dotenv = "/home/code/backend/.env"
path_logs = "/home/code/backend/logs"
max_queue_length = 50
max_thread_workers = 5
batch_size_base = 8
max_documents_to_retrieve_from_es = 250
embedding_models_info = {
    "embedding/BAAI/bge-m3":{
        "dimension": 1024,
        "sequence_length": 8192,
        "recommended_batch_size": 12,
        "original_model": "BAAI/bge-m3"
    },
    "text-embedding-ada-002": {
        "dimension": 1024,
        "sequence_length": 8192,
        "recommended_batch_size": 12,
        "original_model": "BAAI/bge-m3"
    }
}
chunking_methods = {
    "naive_sentence_chunking": {
        "chunk_size": 512,
        "overlap": 0.2
    },
    "naive_word_chunking": {
        "chunk_size": 512,
        "overlap": 0.2
    },
    "semantic_chunking": {}
}