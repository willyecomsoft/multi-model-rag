from unstructured.partition.pdf import partition_pdf
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import os
import base64
from langchain.schema.messages import HumanMessage
import uuid
from llm import create_openai_embeddings
from couchbaseops import insert_doc, get_doc, cluster
from sharedfunctions.print import print_bold
import couchbase.subdocument as subdocument

load_dotenv()

bucket = 'data'
scope = 'uat'

def partition_document(id, path):
    # Extract images, tables, and chunk text
    print_bold("partition_pdf...")
    raw_pdf_elements = partition_pdf(
        filename=path,
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=path + "/.."
    )
    print_bold(f"got {len(raw_pdf_elements)} elements")

    tables = []
    texts = []
    images = []

    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            table_string = str(element)
            tables.append(table_string)
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            text_string = str(element)
            texts.append(text_string)


    # Read images, encode to base64 strings
    # Image summarization
    def encode_image(image_path):
        ''' Getting the base64 string '''
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    path_figures = "figures/"
    for img_file in sorted(os.listdir(path_figures)):
        if img_file.endswith('.jpg'):
            img_path = os.path.join(path_figures, img_file)
            images.append(encode_image(img_path))
            #image_summaries.append(image_summarize(base64_image,prompt))


    # Insert into couchbase
    def insert_into_couchbase(docs, category, ids=None):
        print_bold(f"Inserting {category} into couchbase")

        ''' Inserting into couchbase '''
        for doc in docs:
            #embeddings = create_openai_embeddings(doc)
            doc_to_insert = {
                "file_id": id,
                #"text": doc,
                "category": category
                #"embeddings": embeddings
            }

            if category == "text":
                doc_to_insert['text'] = doc
            elif category == "image" or category == "table":
                doc_to_insert["content"] = doc

            #find the index of doc within docs, and use it to get the corresponding id
            doc_id = ids[docs.index(doc)] if ids else str(uuid.uuid4())
            insert_doc(bucket, scope, "data", doc_to_insert, doc_id)

    insert_into_couchbase(texts,  "text")
    insert_into_couchbase(images, "image")
    insert_into_couchbase(tables, "table")


def describe_img(img_base64):

    print_bold('describing image...')

    prompt = "Describe the image in detail. Be specific about graphs, such as bar plots."

    ''' Image summary '''
    chat = ChatOpenAI(model="gpt-4o", max_tokens=1024)

    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text":prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        },
                    },
                ]
            )
        ]
    )
    return msg.content


def text_summary(text):

    print_bold('summarizing table or text...')

    # Prompt
    prompt_text = """You are an assistant tasked with summarizing tables and text. \
    Give a concise summary of the table or text. Table or text chunk: {element} """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Summary chain
    # open ai
    model = ChatOpenAI(temperature=0, model="gpt-4o")
    summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

    summary = summarize_chain.invoke({'element': text})

    return summary

def do_embedding(doc_id):

    cb_operations = []

    doc = get_doc(bucket, scope, 'data', doc_id)
    category = doc.get('category')
    text = doc.get('text')

    # describe image and table
    if category == "image":
        text = describe_img(doc.get('content'))
        cb_operations.append(subdocument.upsert('text', text))
    elif category == "table":
        text = text_summary(doc.get('content'))
        cb_operations.append(subdocument.upsert('text', text))

    print_bold(f'create embeddings: {doc_id}....')
    embeddings = create_openai_embeddings(text)
    cb_operations.append(subdocument.upsert('embeddings', embeddings))

    cb_collection = cluster.bucket(bucket).scope(scope).collection('data')
    cb_collection.mutate_in(doc_id, cb_operations)

