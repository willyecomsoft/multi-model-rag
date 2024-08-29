<br><br><br>

# Multi-Model RAG with Couchbase

<br><br>

Multi-model RAG is, just, cool. So, let's give it a try with Couchbase as a backend.

This demo is an inspiration from Sudarshan Koirala's fantastic [walk-through](https://www.youtube.com/watch?v=-77EvEjuZJY). And at a high level, here's what's happening (credits to this [awesome video](https://www.youtube.com/watch?v=Rg35oYuus-w))

![image](https://github.com/user-attachments/assets/970fb266-5756-4a8e-ab10-5f5b907da070)



<br>


## What Do I Need to Run This Demo? 
1. an OPENAI api key 

2. 1 virtual machine running Couchbase v7.6 or above. I'll use AWS EC2 but anything with minimal config will do

3. Docker


<br><br>


## Setup

**1.1 LLM & LangSmith**
<br>

GPT-4o is used in this demo. You need to have an **OPENAI_API_KEY** from [OpenAI](https://openai.com/). 


<br><br>

**1.2 VM Deployment**
<br>

Let's create a VM that hosts Couchbase. 

Create a the **Couchbase Node** with the following startup script: 
```
#!/bin/bash
sudo wget https://packages.couchbase.com/releases/7.6.1/couchbase-server-enterprise-7.6.1-linux.x86_64.rpm
yes | sudo yum install ./couchbase-server*.rpm
sudo systemctl start couchbase-server
```
<br>

>🙌🏻 Make sure to update firewall rules setting to allow ALL inbound/outbound traffics.

<br>


Grab the hostname of Couchbase Node and let's create the backend. Access the Couchbase service via this link: 

```
{couchbase_node_dns:8091}
```

You'll be greeted with the screen below. 

![image](https://github.com/user-attachments/assets/2d8fa2d1-7ed1-41e0-bbff-a6907394372a)


<br><br>

Let's setup a new cluster. Note down the **Username** and **Password**

![image](https://github.com/user-attachments/assets/5780c221-de06-4992-8db9-36d6534d3312)


<br><br>

Accept the terms and click "**Configure Disk, Memory, Services**" since we don't need all Couchbase services in this demo. 

![image](https://github.com/user-attachments/assets/69c14b24-184c-487f-ac21-087cef540b79)


<br><br>

Unselect "Analytics", and "Backup". Leave the rest unchanged and click "**Save & Finish**"

![image](https://github.com/user-attachments/assets/6e76df73-e328-48c3-a2e6-5f65b41361d2)


<br><br>

All good! You'll see the empty-ish screen below since we haven't created the data structure. Replacing variables "EE_HOSTNAME" with your VM hostname, "CB_USERNAME" and "CB_PASSWORD" with the credentials you just created, execute the following REST calls to create the data structures we'll use.

```
**1. create "data" bucket, with quota of RAM@ 10,000MB, and flushing enabled**
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=data \
     -d ramQuota=10000 \
     -d bucketType=couchbase \
     -d flushEnabled=1


**2. create "data" scope under "data" bucket**
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=data



**3. lastly, create "data" collection under "data" scope
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes/data/collections \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=data
```

<br>

>🙌🏻 In a production set up you'll need at least 3 nodes to run Couchbase for HA purposes. In our case, let's just use 1 node for simplicity.


For us to effectively run vector & full-text search, we will create a search index under "Search" service. 

![image](https://github.com/user-attachments/assets/66c00519-e6e2-4547-98b7-03567924e854)


<br><br>

Use the "Import" button on the top-right, paste the index definition JSON from **fts-index.json** under templates/assets, and there you go. 

![image](https://github.com/user-attachments/assets/72a84234-ee9f-4066-9a72-48dc3ec409cf)

<br><br>

Click "Create Index" at bottom left to finish creation process.
![image](https://github.com/user-attachments/assets/24e1854f-db22-4c78-aa3b-dd89c5552774)

<br><br>


**1.4 Docker Node Setup**

<br>

At a new project folder, create a .env file: 
```
# LLM Keys
OPENAI_API_KEY={openai_api_key}

# EE Environment Variables 
EE_HOSTNAME={Couchbase_node_hostname}


#Couchbase User Credential
CB_USERNAME={username_created}
CB_PASSWORD={password_created}
```


Then, run the following Docker command to buil a Docker container from the published Image:

```
docker run --env-file .env -d -p 5002:5002 --name cb-multi-model-rag jasoncaocouchbase0812/cb-multi-model-rag:latest
```

<br><br>


All good. The container is now running locally on port 5002. We can run the code below to see live logging:

```
docker logs -f cb-multi-model-rag //replace "cb-multi-model-rag" with the actual container name if modified 
```

<br><br>

<img width="1088" alt="image" src="https://github.com/user-attachments/assets/95d20245-c4fb-4d2a-a75b-b455e58c5205">


<br><br>

## Upload Docs 

<br>

On your browser, access this link below to upload a PFD to chat with. Ideally you'll want to select a document that has texts, tables, and images. To preserve your token consumption, avoid too large documents.

> localhost:5002/upload

I'll be using the [NoSQL Benchmark Report 2023](https://www.couchbase.com/content/capella/altoros-report-eval-nosql-dbaas) produced by Altoros. To decrease my token consumption throughout the demo, I've truncated the document to only include section 4.1, ie., summary for update-heavy workloads, which will be uploaded here. You can find both documents under directory **templates/assets**.  

<br>

![image](https://github.com/user-attachments/assets/c1bcf4a4-4416-4be3-92db-c3c15ed83acd)


<br><br>


**Check Upload Result**

<br>

We're using [Unstructured](https://github.com/Unstructured-IO/unstructured) library for parsing the document and it takes a while to finish. After ~2 minutes, go to Couchbase console, under "Documents", select keyspace **"data"."data"."data"**. There you'll have the parsed documents. Logic here is to store text by a predefined logics, while LLM is used to give summary of images and tables found. All 3 types of information are then stored in Couchbase, along with their embeddings. 

![image](https://github.com/user-attachments/assets/be71380c-cc25-4491-8fd3-65433f6dce4c)


<br><br>

How do we know which how many images, texts chunks, and tables are there? You may notice each document has a **"category"** field, but a structured way to query is preferred. let's go to Query tab. 

Select "data"."data" context from the top right of the Query Editor, enter the familiar SQL query below, and there you go.

<br>

```
SELECT category, COUNT(*) AS count
FROM data
GROUP BY category;
```

<br><br>

![image](https://github.com/user-attachments/assets/30f9c0d6-9c4b-4190-a987-6cdd8f379c27)

<br><br>

If you feel like gaining a bit more insights on your images, run more queries to examine your data: 

<br>

![image](https://github.com/user-attachments/assets/c184d4ae-eb38-41d1-aa2f-323c80a12913)


**Let's ask some questions!**

Go to **localhost:5002** on your browser, and let's have some fun! 

![image](https://github.com/user-attachments/assets/20627287-df47-42b5-a61c-f85884c94609)

Notice under "Source Document Found:", we're given the source of information fed to the LLM. Information of type image, text, or table are given separate icons for indication. Click each icon to expand, and slice & dice further!

