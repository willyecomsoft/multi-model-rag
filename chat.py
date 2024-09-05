from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os 

load_dotenv()
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

llm = Ollama(
    base_url=ollama_base_url, 
    model='qwen2:0.5b',
)

prompt = ChatPromptTemplate.from_template(
    "你是一名廣告行銷專業人員，請提供以下文字的廣告詞：{message}！"
)

chain = prompt | llm

print(chain.invoke({"message": "苦瓜"}))