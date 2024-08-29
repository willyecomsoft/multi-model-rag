# Multi-Model RAG with Couchbase

Multi-model RAG is, just, cool. So, let's give it a try with Couchbase as a backend.


Here's what's happening (credits to this [awesome video](https://www.youtube.com/watch?v=Rg35oYuus-w))

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

Update the Eventing functions endpoints with the hostname of App Node. 

```
python3 updateips.py
```

>🙌🏻 - Eventing is Couchbase's version of Database Trigger and Lambda functions. It's a versatile and powerful tool to stitch together your data processes and achieve high automation.


<br><br>

Set up bucket/scope/collections, fts index, and update the endpoint for the app: 

```
python3 setupservers.py
```

<br>

> ❗️Sometimes the event creation might fail and you would see error message like below:
```
Error importing function process_refund_ticket: 400 Client Error: Bad Request for url:xxxx. 
```

<br>

This could be due to not enough time between bucket and eventing creation. In this case, re-run the command and you'll see the success message: 
```
Importing function process_refund_ticket...
Function process_refund_ticket imported successfully
Importing function process_message... 
Function process_message imported successfully
```

<br><br>

Now let's load some sample data. This includes products, orders, product FAQ, and refund policies. We will see the bot reasoning through the query and interact with the data in the ways deemed fit.

```
python3 reindex.py
```

<br><br>

You should be able to see this success message.

![alt text](static/images/image-5.png)

<br><br>

You can also check the Couchbase console. There should be data in "**orders**", "**products**" and "**policies**" collections under **"main"."data"** keyspace.

![alt text](static/images/image-6.png)

<br><br>

As a last step, let's create some indexes needed for the bot to run queries later. Go to Couchbase console, select **Query** from the left side menu bar, and run the syntaxes below **individually**: 

```
create primary index on `main`.`data`.`policies`
create primary index on `main`.`data`.`products`
create primary index on `main`.`data`.`orders`
create primary index on `main`.`data`.`messages`
create primary index on `main`.`data`.`message_responses`
create primary index on `main`.`data`.`refund_tickets`
```

<br><br>

>🙌🏻 We're creating primary indexes here which only index the document keys, and this is not a recommended indexing behavior in production environment, where more performant and advanced indexing should be employed instead.

<br><br>

All good. Let's go 

```
python3 app.py
```



<br><br>

## Chat with the Bot 

<br>

On your browser, access this link below. You should see the empty chat screen.

> {App_node_hostname}:5001

![image](https://github.com/user-attachments/assets/8eece557-94dd-411c-be39-86e5d9899380)



<br><br>

**Ask Product Questions**

<br>

Let's ask some **product related** questions: 

```
I bought a vacuum and I really liked it! Do you have any washing machines to recommend as well?
```

![image](https://github.com/user-attachments/assets/db9e2dac-6f28-45f8-93f2-95de1bf2c9d5)


Under the hood the bot is sending **SQL queries** to Couchbase to fetch washing machine product info. 

<br><br><br>

Let's ask questions that's trickier than SQL query. Refresh the page, and ask another question.

```
I bought a washing machine and it's starting to smell really bad recently. What should I do? 
```

<br>

![image](https://github.com/user-attachments/assets/568819a3-b117-4de3-b58b-3a9207b13b76)


<br><br>

Other than recommending some products, it's actually looking into the product manuals. Semantic Search and RAG is in play here supported by Couchbase Vector Search. 

<br><br><br>

Let's refresh the page again, and try asking some refund queries: 

```
I bought a washing machine and my order is SO005. It stopped working. I'd like to have a refund please.
```

![image](https://github.com/user-attachments/assets/f486be99-cd08-4648-9a5d-46a6955060fb)


<br><br><br>

The bot is able to deflect invalid refund requests by looking into refund policy, doing some maths and making a sound judgement calls. Now what happens if the refund request is valid? 

```
I bought a vacuum and my order is SO005. It stopped working. I'd like to have a refund please.
```

<br>

![image](https://github.com/user-attachments/assets/b7a6cb7a-9dee-4b65-9429-722d98346f7f)


<br><br>

This time the refund request is deemed valid since washing machine and vacuum have different refund period (you can check under **dataset/faq.txt**, which is indexed into Couchbase). Note the bot even created a refund ticket, which can be found under "main"."data"."refund_tickets" collection in Couchbase.

![Refund Tickets Collection](static/images/image-13.png)

<br><br>


## Beyond the Question Answering

Realistically, the customer service process doesn't end with the initial response provided. A common example is follow-ups on the refund ticket. Let's put on the hat of a Refund Manager and look at the valid requests created by the bot. Access the Refund_Tickets page via: 

> {App_node_hostname}:5001/tickets 

<br>

![alt text](static/images/image-21.png)

Logically, the refund admin looks at the information here, checks out details of everything, and makes a sound judgement on whether the bot-deemed-qualified refund is indeed valid, and the refund amount.

Of course another LLM agent can be set up for this task too, but let’s agree on this: in 2024, it’s still a good call to involve human beings in such decision makings. Let’s approve this refund ticket.

You’ll see a success message. Refresh the page. The update is reflected.

Go back to main page. Another message is sent to the customer on the good news of the refund ticket. Again, [Couchbase Eventing](https://www.couchbase.com/products/eventing/) doing its real time process stitching. 


![image](https://github.com/user-attachments/assets/5bef29ad-954d-4d47-877e-3daf70e0b84c)


<br><br>

Let’s go to “Customer Message” tab. 

> {App_node_hostname}:5001/messages 

<br>

![alt text](static/images/image-23.png)


Note each message has been labelled a sentiment, and a category. We’re leveraging LLM to apply metadata here, but again, Eventing is making this automation smooth as butter.

<br><br>

## Traceability 

We all know LLM cannot be fully deterministic at the moment. That is why, if we entrust the reasoning process to a bot, we need to have full visibility on its reasoning process. 

Note how every response from the bot has a "trace" link provided. Let's click the link, which will take us to the LangSmith page where this reasoning process is broken down to details.

<br>

![image](https://github.com/user-attachments/assets/40a0d263-c74c-4070-aa96-99421f90ed22)


<br><br>

With first-time access, you'll be prompted to login. Use the same credentials for which you created the LangChain API key. 

![alt text](static/images/image-24.png)

<br><br>

You should be able to see something like this:

![alt text](static/images/image-25.png)


LangSmith is an awesome tool for understanding and troubleshooting the agentic process. Note in our workflow, we have define 5 agents: 

- General-support agent that gathers info of order and products mentioned, and generate an initial response 
- Recommendation agent that searches and recommends products
- Product_fix agent that searches the FAQ library for any product-related queries 
- Refund agent that reasons through whether refund requests, if raised, is valid 
- And a Finalizer agent that takes all info gathered previously, and generate a professional and relevant response based on customer query. 


<br><br>

Drill into any step during the reasoning chain, look at the input/output. I find it amazing at even optimizing my workflows!

![alt text](static/images/image-26.png)

