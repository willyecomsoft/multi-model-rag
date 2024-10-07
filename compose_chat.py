from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os 
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.schema.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)

prompt = ChatPromptTemplate.from_template("""Answer the following question incorporating the following context:
<context>
{context}
</context>

The answer should be precise and professional, and no longer than 5 sentences. 

Question: {input}""")


def prompt_func(dict):
    # concatenate texts
    format_texts = "\n\n".join(dict["context"]["texts"])

    # initiate the context dict for the prompt
    content = [
        {
            "type": "text", 
            "text": f"""Answer the question based only on the following context, which can include text, tables, and the below image:
                Question: {dict["question"]}

                Text and tables:
                {format_texts}
            """
        }
    ]

    return [
        HumanMessage(
            content=content
        )
    ]

chain = RunnableLambda(prompt_func) | llm | StrOutputParser()

text = [
      "aaabbbccc is a framwork",
      "aaabbbccc is a developed by abc corp.",
      "使用aaabbbccc 可以簡化ai程式的開發"
]

context_to_pass = {
    "context": {
        "texts": text
    },
    "question": "aaabbbccc是什麼?"
}

message_string = ""  
for chunk in chain.stream(context_to_pass):
        message_string += chunk

print(message_string)
