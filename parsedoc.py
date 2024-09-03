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
from couchbaseops import insert_doc
from sharedfunctions.print import print_bold
import sys

load_dotenv()

path = "content/"
file_name = "document.pdf"


def partition_document():
    # Extract images, tables, and chunk text
    raw_pdf_elements = partition_pdf(
        filename=path + file_name,
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=path,
    )
    print_bold(f"got {len(raw_pdf_elements)} elements")

#     tables = []
#     texts = []
#
#     for element in raw_pdf_elements:
#         if "unstructured.documents.elements.Table" in str(type(element)):
#             tables.append(str(element))
#         elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
#             texts.append(str(element))
#
#
#     # Prompt
#     prompt_text = """You are an assistant tasked with summarizing tables and text. \
#     Give a concise summary of the table or text. Table or text chunk: {element} """
#     prompt = ChatPromptTemplate.from_template(prompt_text)
#
#     # Summary chain
#     model = ChatOpenAI(temperature=0, model="gpt-4o")
#     summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()
#
#     # Apply to text
#     # Typically this is reccomended only if you have large text chunks
#     text_summaries = texts # Skip it
#
#     # Apply to tables
#     table_summaries = summarize_chain.batch(tables, {"max_concurrency": 5})
#
#     # Image summarization
#     def encode_image(image_path):
#         ''' Getting the base64 string '''
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode('utf-8')
#
#     def image_summarize(img_base64,prompt):
#         ''' Image summary '''
#         chat = ChatOpenAI(model="gpt-4o",
#                         max_tokens=1024)
#
#         msg = chat.invoke(
#             [
#                 HumanMessage(
#                     content=[
#                         {"type": "text", "text":prompt},
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/jpeg;base64,{img_base64}"
#                             },
#                         },
#                     ]
#                 )
#             ]
#         )
#         return msg.content
#
#     # Store base64 encoded images
#     img_base64_list = []
#
#     # Store image summaries
#     image_summaries = []
#
#     # Prompt
#     prompt = "Describe the image in detail. Be specific about graphs, such as bar plots."
#
#     path_figures = "figures/"
#
#     # Read images, encode to base64 strings
#     for img_file in sorted(os.listdir(path_figures)):
#         if img_file.endswith('.jpg'):
#             img_path = os.path.join(path_figures, img_file)
#             base64_image = encode_image(img_path)
#             img_base64_list.append(base64_image)
#             image_summaries.append(image_summarize(base64_image,prompt))
#
#
#     # Insert into couchbase
#     def insert_into_couchbase(docs, category, ids=None):
#         print_bold(f"Inserting {category} into couchbase")
#
#         ''' Inserting into couchbase '''
#         for doc in docs:
#             embeddings = create_openai_embeddings(doc)
#             doc_to_insert = {
#                 "text": doc,
#                 "category": category,
#                 "embeddings": embeddings
#             }
#
#             if category == "image_summary":
#                 doc_to_insert["content"] = img_base64_list[docs.index(doc)]
#             elif category == "table_summary":
#                 doc_to_insert["content"] = tables[docs.index(doc)]
#
#             #find the index of doc within docs, and use it to get the corresponding id
#             doc_id = ids[docs.index(doc)] if ids else str(uuid.uuid4())
#             insert_doc("data", "data", "data", doc_to_insert, doc_id)
#
#     insert_into_couchbase(text_summaries,  "text_summary")
#     insert_into_couchbase(image_summaries, "image_summary")
#     insert_into_couchbase(table_summaries, "table_summary")