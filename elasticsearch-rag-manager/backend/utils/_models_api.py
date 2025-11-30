"""
All the code related to LLM models will be done here.
text-generation/embedding

"""
import os
from dotenv import load_dotenv
import aiohttp
import json
from openai import OpenAI
import requests

load_dotenv()


class _fastchat_openai_api:
    def __init__(self, logger):
        self.base_url = os.getenv("CUSTOM_OPENAI_IP_V1")
        self.client = self.initialize_openai_api()
        self.logger = logger


    def initialize_openai_api(self):
        # client = OpenAI(api_key=os.getenv("CUSTOM_OPENAI_API_KEY"))
        client = OpenAI(base_url=os.getenv("CUSTOM_OPENAI_IP_V1"), api_key=os.getenv("CUSTOM_OPENAI_API_KEY"))
        return client


    async def get_models_list(self):
        """
        model_type: str, all/text-generation/embedding
        """
        url = self.base_url + os.getenv("CUSTOM_OPENAI_MODEL_LIST")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                models_list = await res.text()
        models_list = json.loads(models_list)
        # models_list = [data["id"] for data in models_list["data"]]
        return models_list

    def get_models_list_sync(self):
        """
        model_type: str, all/text-generation/embedding
        """
        url = self.base_url + os.getenv("CUSTOM_OPENAI_MODEL_LIST")
        models_list = requests.get(url).text
        # print(models_list)
        models_list = json.loads(models_list)
        models_list = [data["id"] for data in models_list["data"]]
        return models_list



    def inference(self, model_name, text):
        """
        model_name: str, the name of the model
        text: str, the text to be generated
        """
        pass


    def embedding(self, model_name, text_list):
        """
        model_name: str, the name of the model
        text: list[str], the text to be embedded

        return: list
        """
        embedding_results = self.client.embeddings.create(model=model_name, input=text_list)
        embedding_results = embedding_results.data
        embedding_results = [embedding_result.embedding for embedding_result in embedding_results]
        return embedding_results

        # outputs = []
        # for i in range(0, len(text_list), batch_size):
        #     texts = text_list[i:i+batch_size]
        #     embedding_results = self.client.embeddings.create(model=model_name, input=texts)
        #     embedding_results = embedding_results.data
        #     for text, embedding_result in zip(texts, embedding_results):
        #         _pair = {}
        #         _pair["text"] = text
        #         _pair["vector"] = embedding_result.embedding
        #         outputs.append(_pair)

        # return outputs