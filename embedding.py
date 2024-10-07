from langchain_community.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
import os 
from openai import OpenAI

load_dotenv()
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

client_openai = OpenAI()

def create_embedding(text = 'hello'):
    print(text)
    emb = OllamaEmbeddings(
        base_url=ollama_base_url, 
        model='qwen2:1.5b',
    )

    #qwen2同時也是embedding model
    embedding = emb.embed_documents(text)
    return embedding[0]

def create_openai_embeddings(input_message):
    return client_openai.embeddings.create(input = [input_message], model="text-embedding-ada-002").data[0].embedding

if __name__ == '__main__':
    print(create_embedding())