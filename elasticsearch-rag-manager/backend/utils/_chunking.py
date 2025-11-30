import re
import numpy as np
from semantic_router.encoders import OpenAIEncoder
from semantic_router.splitters import RollingWindowSplitter
from utils._helper import transform_dict_n_str
import os
from dotenv import load_dotenv
import config as cfg

load_dotenv(cfg.path_dotenv)

def set_template():
    template = {
        "document_title": None,
        "document_type": None,
        "content_index": None,
        "content": None,
        "content_index_type": None
    }
    return template

class naive_sentence_chunking:
    def __init__(self, logger, chunk_size=512, overlap=0.2):
        self.chunk_size = chunk_size # max tokens
        self.overlap = overlap
        self.logger = logger


    def check(self):
        if self.chunk_size < 1:
            return False
        return True

    def set_instance_variable(self, info):
        self.chunk_size = info["chunk_size"]
        self.overlap = info["overlap"]

    def start(self, retrieved_text:dict):
        chunked_text_list = []

        template = set_template()
        template["document_title"] = retrieved_text["document_title"]
        template["document_type"] = retrieved_text["document_type"]
        template["content_index_type"] = retrieved_text["contents_index_type"]


        for idx, content in retrieved_text["contents"].items(): 
            if "text" not in content:
                continue
            template["content"] = {}
            template["content_index"] = idx
            chunked_text = ""

            # sentences = re.split(r'(?<=\.) ', content["text"])
            sentences = re.split(r'(?<=\.) |\n', content["text"])
            max_tokens = 0
            total_tokens = 0
            for sentence in sentences:
                total_tokens += len(sentence.split(" "))
                max_tokens = max(max_tokens, len(sentence.split(" ")))   
            for sentence in sentences:
                tokens_in_sentence = sentence.split(" ")
                if len(chunked_text.split(" ")) + len(tokens_in_sentence) < self.chunk_size:
                    chunked_text += sentence + " "
                else:
                    template["content"] = {"text":chunked_text.strip()}
                    chunked_text = sentence
                    chunked_text_list.append(transform_dict_n_str(template, dict_2_str=True))

            template["content"] = {"text":chunked_text.strip()}
            chunked_text_list.append(transform_dict_n_str(template, dict_2_str=True))

        return chunked_text_list


class naive_word_chunking:
    def __init__(self, chunk_size=512, overlap=0.2):
        self.chunk_size = chunk_size # max tokens
        self.overlap = overlap
    

    def check(self):
        if self.chunk_size < 1:
            return False
        if self.overlap < 0 or self.overlap >= 1:
            return False
        return True

    def set_instance_variable(self, info):
        self.chunk_size = info["chunk_size"]
        self.overlap = info["overlap"]

    def start(self, retrieved_text:dict):
        chunked_texts = []
        for content in retrieved_text:
            tokens = np.array(content.split(" "))
            overlap = int(self.chunk_size * self.overlap)
            indices = np.arange(0, len(tokens), self.chunk_size - overlap)
            chunked_text = [" ".join(tokens[i:i + self.chunk_size]) for i in indices]

        return chunked_texts


class semantic_chunking:
    def __init__(self, 
                embedding_model=None, 
                threshold=0.2, 
                chunk_base="sentence", 
                max_tokens=256, 
                min_tokens=32, 
                min_base_chunks=2,
                num_overlap_base_chunks=1,
                split_window_size=1,
                integrate_doc=True,
                logger=None
                ):
        self.embedding_model = embedding_model
        self.threshold = threshold # (-1, 1)
        self.chunk_base = chunk_base
        self.max_tokens = max_tokens 
        self.min_tokens = min_tokens
        self.min_base_chunks = min_base_chunks
        self.num_overlap_base_chunks = num_overlap_base_chunks
        self.split_window_size = split_window_size
        self.integrate_doc = integrate_doc
        self.logger = logger


    def check(self):
        if self.chunk_base not in ["sentence", "word", "paragraph"]:
            return False
        if self.max_tokens < 1 or self.min_tokens < 1 or self.max_tokens < self.min_tokens:
            return False
        if self.min_base_chunks <= self.num_overlap_base_chunks:
            return False
        return True


    def set_instance_variable(self, info):
        self.embedding_model = info["embedding_model"]
        self.threshold = info.get("threshold", 0.2)
        self.chunk_base = info.get("chunk_base", "sentence")
        self.max_tokens = info.get("max_tokens", 2048)
        self.min_tokens = info.get("min_tokens", 32)
        self.min_base_chunks = info.get("min_base_chunks", 2)
        self.num_overlap_base_chunks = info.get("num_overlap_base_chunks", 1)
        self.split_window_size = info.get("split_window_size", 1)


    def start(self, retrieved_text:dict):
        encoder = OpenAIEncoder(
            name=self.embedding_model, 
            openai_api_key=os.getenv("CUSTOM_OPENAI_API_KEY"),
            openai_base_url=os.getenv("CUSTOM_OPENAI_IP_V1")
            )

        if self.threshold < 0:
            dynamic_threshold = True
        else:
            dynamic_threshold = False       

        splitter = RollingWindowSplitter(encoder=encoder, 
                                         dynamic_threshold=dynamic_threshold,
                                         max_split_tokens=self.max_tokens, 
                                         min_split_tokens=self.min_tokens,
                                         window_size=self.split_window_size,
                                         plot_splits=False,
                                         enable_statistics=False)
        
        template = set_template()
        template["document_title"] = retrieved_text["document_title"]
        template["document_type"] = retrieved_text["document_type"]
        template["content_index_type"] = retrieved_text["contents_index_type"]

        chunked_text_list = []

        if self.integrate_doc:
            # Integrate all retrieved_text into one
            template["content_index"] = "integrated"
            
            chunked_text = ""
            for idx, content in retrieved_text["contents"].items():
                if "text" not in content:
                    continue
                chunked_text += content["text"]
            
            splits = splitter([chunked_text])
            for chunk in splits:
                chunk = " ".join(chunk.docs)
                template["content"] = {"text":chunk}
                chunked_text_list.append(transform_dict_n_str(template, dict_2_str=True))
            
        else:
            for idx, content in retrieved_text["contents"].items():
                template["content"] = {}
                template["content_index"] = idx
                chunked_text = ""

                splits = splitter([content["text"]])
                for chunk in splits:
                    chunk = " ".join(chunk.docs)
                    template["content"] = {"text":chunk}
                    chunked_text_list.append(transform_dict_n_str(template, dict_2_str=True))

        return chunked_text_list