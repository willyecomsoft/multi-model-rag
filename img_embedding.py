import requests
from PIL import Image
url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

from imgbeddings import imgbeddings
ibed = imgbeddings()

embedding = ibed.to_embeddings(image).tolist()[0]

import io
import base64
buffer = io.BytesIO()
image.save(buffer, format=image.format)
image_bytes = buffer.getvalue()
image_base64 = base64.b64encode(image_bytes).decode('utf-8')

doc = {
    "type": "image",
    "name": "test",
    "content": image_base64,
    "embeddings": embedding
}

from insertdoc import insert_doc
insert_doc('data', 'data', 'data', doc)
