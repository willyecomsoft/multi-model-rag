# What will we use in this workshop?

1. openai
2. local ai 
    1. [Ollama](https://github.com/ollama/ollama)
        - qwen2:0.5b
        - qwen2:1.5b
    2. open-webui
3. couchbase
4. python
5. vsCode
6. postman


## Setup step
**0. docker**

```
docker network create -d bridge workshop-net
```

**1. OPENAI**

prepare your OPENAI_API_KEY from [OpenAI.](https://platform.openai.com/api-keys)

<br>

**2. couchbase**

follow [couchbase_setup.md](./couchbase_setup.md)

<br>

**3. dev env**

```
git clone https://github.com/willyecomsoft/multi-model-rag.git
cd multi-model-rag
git checkout workshop
```

<br>

check .env.example and create  a .env file
```
# LLM Keys
OPENAI_API_KEY={openai_api_key}

OLLAMA_BASE_URL=http://ollama:11434

# EE Environment Variables 
EE_HOSTNAME=couchbase


#Couchbase User Credential
CB_USERNAME=admin
CB_PASSWORD=workshop
CB_SCOPE=uat
```

then follow [dev_setup.md](./dev_setup.md)

<br>

**4. local ai**

follow [local_ai.md](./local_ai.md)