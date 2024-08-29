from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from llm import chain, multi_model_search, model, prompt_func, generate_query_transform_prompt
import time
from langchain.schema.runnable import RunnableLambda
import os 
from sharedfunctions.print import print_error, print_success, print_bold
from parsedoc import partition_document
from couchbaseops import run_query

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

demo_ephemeral_chat_history = ChatMessageHistory()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_existing_data')
def check_existing_data():
    return render_template('check_existing_data.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@socketio.on('message')
def run_multi_model_search(question_data):
    
    # vector search and return results
    question = question_data["question"]
    
    # add message to chat history
    demo_ephemeral_chat_history.add_user_message(question)
    
    # generate new query
    new_query = generate_query_transform_prompt(demo_ephemeral_chat_history.messages)
    print(f"Generated query: {new_query}")
    
    # run multi model search
    doc_ids, documents, b64, text = multi_model_search(new_query)
    
    # emit message back to html to display reference docs
    socketio.emit("found_docs", {
        "doc_ids": doc_ids,
        "documents": documents
    })
    
    # define contexts to pass
    context_to_pass = {
        "context": {
            "images": b64,
            "texts": text
        },
        "question": question
    }

    # define final chain
    final_chain = (
        RunnableLambda(prompt_func)
        | chain
    )

    # stream 
    message_string = ""   
    timestamp = int(time.time())
    
    for chunk in final_chain.stream(context_to_pass):
        message_string += chunk
        
        socketio.emit('response', {
            "message_string": message_string,
            "timestamp": timestamp,
        })
    
    #6. add bot message, both locally and to couchbase
    demo_ephemeral_chat_history.add_ai_message(message_string)

@app.route('/parse_document', methods=['POST'])
def parse_document():
    
    # Delete existing data 
    query = """
        DELETE FROM `data`.`data`.`data`     
    """
    
    run_query(query, True)
    
    # Ensure the "content" directory exists
    print_bold(f"getting payload: {request.files}")
    content_dir = os.path.join(os.getcwd(), 'content')
    os.makedirs(content_dir, exist_ok=True)

    # Get the file from the request
    file = request.files['file']

    # Define the path to save the file
    file_name = 'document.pdf'
    save_path = os.path.join(content_dir, file_name)
    
    # Save the file to the "content" directory
    file.save(save_path)
    print_success('File saved')
    
    # start partitioning
    partition_document()
    
    return jsonify({"message": f"File saved to {save_path}"}), 200
    
  

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002)