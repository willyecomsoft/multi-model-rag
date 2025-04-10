import pymupdf4llm
import json
import time
from pathlib import Path
import shutil
from couchbaseops import insert_doc
from dotenv import load_dotenv
import os
import uuid
import base64
import re

load_dotenv()

bucket = 'data'
scope = os.getenv("CB_SCOPE")


def encode_image(image_path):
    ''' Getting the base64 string '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

# Helper to split text in half
def split_half(text):
    mid = len(text) // 2
    return text[:mid], text[mid:]


def create_blended_doc(prev_doc, curr_doc, prev_index, curr_index):
    prev_text = prev_doc["text"]
    curr_text = curr_doc["text"]

    _, prev_half = split_half(prev_text)
    curr_half, _ = split_half(curr_text)

    blended_text = prev_half + curr_half

    blended_element = {
        **prev_doc,
        "text": blended_text,
        "metadata": {
            **prev_doc.get("metadata", {}),
            "type": "interpolated",
            "between_pages": [prev_index + 1, curr_index + 1]
        }
    }

    return blended_element


def partition_document(file_id, pdf_path):
    print(f"partition_pdf - {pdf_path}")
    
    filename = os.path.basename(pdf_path)

    image_path = str(time.time())

    elements = pymupdf4llm.to_markdown(
        doc=pdf_path,
        page_chunks=True,
        write_images=True,
        image_format="jpg",
        image_path=image_path,
        show_progress=True
    )

    docs = []
    prev_doc = None
    prev_index = -1

    for i, element in enumerate(elements):
        doc = {
            "file_id": file_id,
            "metadata": element.get('metadata', None),
            "category": "text",
            "text": element.get('text', ''),
        }
        if prev_doc:
            blended_doc = create_blended_doc(prev_doc, doc, prev_index, i)
            insert_doc(bucket, scope, "data", blended_doc)

        docs.append(doc)
        prev_doc = doc
        prev_index = i

        insert_doc(bucket, scope, "data", doc)


    for img_file in sorted(os.listdir(image_path)):
        match = re.match(fr"{filename}-(\d+)-\d+\.jpg", img_file)
        if match:
            number = int(match.group(1))
            doc = docs[number]
            doc['category'] = "image"
            doc["content"] = encode_image(os.path.join(image_path, img_file))
            #insert_doc(bucket, scope, "data", doc, str(uuid.uuid4()))


    directory = Path(image_path)
    if directory.exists() and directory.is_dir():
        shutil.rmtree(directory)  # 刪除目錄及其所有內容
        print(f"已刪除目錄及其內容: {image_path}")


        
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\[Partial]2023-Altoros-NoSQL-Dbaas-Performance-Capella-Atlas-Dynamo-Redis-pages.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\605385_112Q4_合併_完稿財報-電子書.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\豐收款線上收款API開發規格書_V1.23.pdf"
#pdf_path = "/Users/willy/Desktop/project/Couchbase/TechmanRobot/OneDrive_1_2025-3-28/605385_112Q4_合併_完稿財報-電子書.pdf"
pdf_path = '/Users/willy/Desktop/project/Couchbase/TechmanRobot/OneDrive_1_2025-3-28/TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf'#

#partition_document("ddd", pdf_path)
