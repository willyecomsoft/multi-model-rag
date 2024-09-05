from embedding import create_embedding
from insertdoc import insert_doc


text = 'aaabbbccc is the framework for building context-aware reasoning applications'
embedding = create_embedding(text)

doc = {
    "type": "test_embedding",
    "name": "test",
    "content": "this is a test string",
    "text": text,
    "embeddings": embedding
}

insert_doc('data', 'data', 'data', doc)
