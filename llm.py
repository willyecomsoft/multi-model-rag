from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.messages import HumanMessage
from base64 import b64decode
from couchbaseops import cb_vector_search


load_dotenv()


chat_openai = ChatOpenAI(model="gpt-4o", temperature=0.05)    

client_openai = OpenAI()

prompt_openai = ChatPromptTemplate.from_template("""Answer the following question incorporating the following context:
<context>
{context}
</context>

The answer should be precise and professional, and no longer than 5 sentences. 

Question: {input}""")


query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        ),
    ]
)

def create_openai_embeddings(input_message):
    return client_openai.embeddings.create(input = [input_message], model="text-embedding-ada-002").data[0].embedding


def generate_query_transform_prompt(messages):
    query_transformation_chain = query_transform_prompt | chat_openai
    
    print("generating transformed query...")
    return query_transformation_chain.invoke({"messages": messages}).content 
    

def generate_document_chain():     
    return create_stuff_documents_chain(chat_openai, prompt_openai)


# run cb vector search
def multi_model_search(question):
    question_vector = create_openai_embeddings(question)
    result = cb_vector_search("data", "data", "search-data", "embeddings", question_vector, ['category', 'content', 'text'])

    b64 = []
    text = []
    doc_ids = []
    documents = []

    for row in result.rows():
        doc_ids.append(row.id)
        
        fields = row.fields
        documents.append(fields)
        
        category = fields["category"]
        content = fields["text"] if category == "text_summary" else fields["content"]
        
        try: 
            b64decode(content)
            b64.append(content)
        except Exception as e:
            text.append(content)
        
    return doc_ids, documents, b64, text


def prompt_func(dict):
    format_texts = "\n".join(dict["context"]["texts"])
    
    images = dict["context"]["images"]
    
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
    
    for image in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                },
            }
        )
    
    
    return [
        HumanMessage(
            content=content
        )
    ]

model = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)


# RAG pipeline
chain = (
    model
    | StrOutputParser()
)




