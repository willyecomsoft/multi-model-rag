# Dev env Setup

>you can user local python or docker

### 1. Local python

install python version >= 3.9


```
cd multi-model-rag
python3 -m venv venv
source venv/bin/activate
```

run in venv
```
pip install -r requirements.txt
python app.py
```

<br>

install poppler-utils
install tesseract-ocr

<br>

![app.png](/static/images/app.png)

### 2. docker

```
cd multi-model-rag
docker build -t cb-multi-model-rag .
```

```
docker run --env-file .env -d -p 5002:5002 --name cb-multi-model-rag cb-multi-model-rag
```