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


def partition_document(file_id, pdf_path, filename="data.pdf"):
    print("partition_pdf...")

    image_path = str(time.time())

    elements = pymupdf4llm.to_markdown(
        doc=pdf_path,
        filename=filename ,
        page_chunks=True,
        write_images=True,
        image_format="jpg",
        image_path=image_path,
        show_progress=True
    )

    docs = []
    for i, element in enumerate(elements):
        doc = {
            "file_id": file_id,
            "metadata": element.get('metadata', None),
            "category": "text",
            "text": element.get('text', ''),
        }
        docs.append(doc)
        insert_doc(bucket, scope, "data", doc)


    for img_file in sorted(os.listdir(image_path)):
        match = re.match(fr"{filename}-(\d+)-\d+\.jpg", img_file)
        if match:
            number = int(match.group(1))
            doc = docs[number]
            doc['category'] = "image"
            doc["content"] = encode_image(os.path.join(image_path, img_file))
            insert_doc(bucket, scope, "data", doc, str(uuid.uuid4()))


    directory = Path(image_path)
    if directory.exists() and directory.is_dir():
        shutil.rmtree(directory)  # 刪除目錄及其所有內容
        print(f"已刪除目錄及其內容: {image_path}")


        
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\[Partial]2023-Altoros-NoSQL-Dbaas-Performance-Capella-Atlas-Dynamo-Redis-pages.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\605385_112Q4_合併_完稿財報-電子書.pdf"
#pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\豐收款線上收款API開發規格書_V1.23.pdf"
#pdf_path = "/Users/willy/Desktop/project/Couchbase/TechmanRobot/OneDrive_1_2025-3-28/605385_112Q4_合併_完稿財報-電子書.pdf"

#partition_document("ddd", pdf_path)
