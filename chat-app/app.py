print('starting chat-app')

import os, json
import gradio as gr
import gradio_client
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline
from langchain.llms import HuggingFaceTextGenInference
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores.pgvector import PGVector
from langchain.callbacks import streaming_stdout
from huggingface_hub import InferenceClient

print('gradio version: {gradio_version}'.format(gradio_version=gr.__version__))
print('gradio_client version: {gradio_client_version}'.format(gradio_client_version=gradio_client.__version__))
# url = "http://{hostname}:{port}".format(hostname=os.environ.get("HOSTNAME"), port=os.environ.get("PORT"))
# client = InferenceClient(model=url)


def get_embeddings():
    print('start: loading embeddings to {path}', os.getenv("SENTENCE_TRANSFORMERS_HOME"))
    # Load sentence transformer embeddings
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device":"cpu"} # use {"device":"cuda"} for distributed embeddings
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

def get_connection_string():
    print('start: getting connection string for vectordb at {hostname}:{port}'.format(hostname=os.environ.get("PGVECTOR_HOST", "localhost"), port=os.environ.get("PGVECTOR_PORT", "5432")))
    return PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("PGVECTOR_HOST", "localhost"),
        port=int(os.environ.get("PGVECTOR_PORT", "5432")),
        database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
        user=os.environ.get("PGVECTOR_USER", "postgres"),
        password=os.environ.get("PGVECTOR_PASSWORD", "secretpassword"),
    )

def get_vector_store(collection_name, connection_string, embeddings):
    print('start: getting vectorstor for {collection_name} using connection')
    store = PGVector.from_existing_index(
        collection_name=collection_name,
        connection_string=connection_string,
        embedding=embeddings,
    )
    return store

def get_prompt_template():
    print('start: getting prompt template')
    prompt_template = """[INST] You are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. Always answer as helpfully as possible, while being safe.
            Use the following pieces of context to answer the question. If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            {context}

            Question: {question}
            Answer:[/INST]"""
    return PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

def get_llm(hostname, port):
    print('start: getting llm')
    callbacks = [streaming_stdout.StreamingStdOutCallbackHandler()]
    return HuggingFaceTextGenInference(
    inference_server_url="http://{hostname}:{port}/".format(hostname=hostname,port=port),
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
    streaming=True,
    callbacks=callbacks
)

def get_llm_client(hostname, port):
    inference_server_url="http://{hostname}:{port}/".format(hostname=hostname,port=port)
    return InferenceClient(model=inference_server_url)

def get_retriever(store, llm, prompt_template):
    print('start: getting retriever')
    retriever = store.as_retriever()
    chain_type_kwargs = {"prompt": prompt_template}

    return RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        verbose=True,
    )



#vector-store
store = PGVector.from_existing_index(
        collection_name=os.getenv("COLLECTION_NAME",'kubernetes_concepts'),
        connection_string=get_connection_string(),
        embedding=get_embeddings(),
    )

llm_client = get_llm_client(os.getenv("TGI_HOSTNAME",'localhost'), int(os.environ.get("TGI_PORT", "8080")))
#connect to pgvector
#store = get_vector_store('kubernetes_concepts', get_connection_string(), get_embeddings())()
# llm = get_llm(os.getenv("TGI_HOSTNAME",'localhost'), int(os.environ.get("TGI_PORT", "8080")))
# retriever = get_retriever(store, llm, get_prompt_template())

def get_doc_data(docs):
    doc_data = []
    for doc in docs:
        doc_json = doc.to_json()
        doc_data.append({
            "page_content": doc_json['kwargs']['page_content'],
            "source": doc_json['kwargs']['metadata']['source']
        })
    return doc_data

def get_content(docs_data):
    content = ""
    for d in docs_data:
        content += "\n" + d["page_content"] + " \n"
    return content

def get_references(docs_data, max_results=1):
    references = ""
    for i, d in enumerate(docs_data):
        references += "\n" + d["source"]
        if i + 1 == max_results:
            break
    return references

def inference(message, history):
    print('inference request with message: {message}'.format(message=message))
    result_docs = store.similarity_search(message)
    print(result_docs)
    docs_data = get_doc_data(result_docs)
    if len(result_docs) > 0:
        # result_docs = result_docs.to_json()
        print('results count: {count}'.format(count=len(result_docs)))
        context = result_docs[0].to_json()['kwargs']
    else:
        print('no results returned')
        context = ""
    full_prompt_llama = """[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. Always answer as helpfully as possible, while being safe.  Use the following context in your response and try to keep your response to 200 words or less.\n
        \n \
        {context} \
        \n
        \n<</SYS>>\n{message}[/INST]""".format(context=context, message=message)
    full_prompt_mistal = """[INST] You are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. 
        Always answer as helpfully as possible, while being safe.  Use the following context in your response and try to keep your response to 200 words or less.\n
        \n \
        {context} \
        \n
        {message} [/INST]""".format(context=context, message=message)
    plants_full_prompt_mistal = """[INST] You are a garden who has been trained to provide helpful, respectful and honest answers about yourself and garden plants. Always answer as helpfully as possible, while being safe.  Use the following context in your response and try to keep your response to 200 words or less.\n
        \n \
        {context} \
        \n
        {message} [/INST]""".format(context=context, message=message)
    
    print(full_prompt_mistal)
    partial_message = ""
    for token in llm_client.text_generation(plants_full_prompt_mistal, max_new_tokens=400, stream=True):
        partial_message += token
        yield partial_message + "\n\n references:{reference_url}".format(reference_url=get_references(docs_data))
# def retrieve_from_chain(message, history):
#     partial_message = "" #TODO: add context (vector) references to the end
#     for token in llm.run(message):
#         partial_message += token
#         yield partial_message

gr.ChatInterface(
    inference,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Chat with me!", container=False, scale=7),
    description="This is the demo for a {model_name} model running on Google Kubernetes Engine".format(model_name=os.environ.get("MODEL_NAME","Mistral 7B")),
    title="Open LLMs on Google Kubernetes Engine",
    examples=["Should I use gateway API in my app?","What is a deployment?"],
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
).queue().launch(share=False,server_port=7860)