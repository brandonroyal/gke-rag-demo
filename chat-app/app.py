import os
import gradio as gr
from huggingface_hub import InferenceClient

url = "http://{hostname}:{port}".format(hostname=os.environ.get("HOSTNAME"), port=os.environ.get("PORT"))
client = InferenceClient(model=url)

def inference(message, history):
    full_prompt_llama = "[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. \
        Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. \
        If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.  Try to keep your response to 200 words or less.\n<</SYS>>\n{message}[/INST]".format(message=message)
    full_message_mistal = "[INST] You are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. \
        Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. \
        If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Try to keep your response to 200 words or less. [/INST] {message}".format(message=message)
    partial_message = ""
    for token in client.text_generation(full_message_mistal, max_new_tokens=200, stream=True):
        partial_message += token
        yield partial_message

gr.ChatInterface(
    inference,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Chat with me!", container=False, scale=7),
    description="This is the demo for a {model_name} model running on Google Kubernetes Engine".format(model_name=os.environ.get("MODEL_NAME")),
    title="Open LLMs on Google Kubernetes Engine",
    examples=["How do I deploy an Llama 2 to Kubernetes?"],
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
).queue().launch()