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
import sys
from sharedfunctions.print import print_bold

load_dotenv()

# Define the chat model
chat_openai = ChatOpenAI(model="gpt-4o", temperature=0.05)    

# Define the OpenAI client
client_openai = OpenAI()

# Define the prompt templates
prompt_openai = ChatPromptTemplate.from_template("""Answer the following question incorporating the following context:
<context>
{context}
</context>

The answer should be precise and professional, and no longer than 5 sentences. 

Question: {input}""")


# Create embeddings
def create_openai_embeddings(input_message):
    return client_openai.embeddings.create(input = [input_message], model="text-embedding-ada-002").data[0].embedding

# Define the query transform prompt
query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        ),
    ]
)

# Generate the query transformation prompt
def generate_query_transform_prompt(messages):
    query_transformation_chain = query_transform_prompt | chat_openai
    
    print_bold("generating transformed query...")
    return query_transformation_chain.invoke({"messages": messages}).content 
    
# Generate the document chain
def generate_document_chain():     
    return create_stuff_documents_chain(chat_openai, prompt_openai)


# run cb vector search
def multi_model_search(question):
    question_vector = create_openai_embeddings(question)
    result = cb_vector_search("data", "uat", "search-data", "embeddings", question_vector, ['category', 'content', 'text'])

    b64 = []
    text = []
    doc_ids = []
    documents = []

    for row in result.rows():
        doc_ids.append(row.id)
        
        fields = row.fields
        documents.append(fields)
        
        category = fields["category"]
        content = fields["text"] if category == "text" else fields["content"]
        
        try: 
            b64decode(content)
            b64.append(content)
        except Exception as e:
            text.append(content)
        
    return doc_ids, documents, b64, text

# Define the final prompt including images, tables, and texts
def prompt_func(dict):
    # concatenate texts
    format_texts = "\n".join(dict["context"]["texts"])
    
    # get images
    images = dict["context"]["images"]
    
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
    
    # for every image found, append the image to the content
    for image in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                },
            }
        )
    
    # return the content as a HumanMessage
    return [
        HumanMessage(
            content=content
        )
    ]

# Define the chat model
model = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)


# RAG pipeline
chain = (
    model
    | StrOutputParser()
)




