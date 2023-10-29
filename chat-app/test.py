import os, sys
import gradio as gr
from huggingface_hub import InferenceClient
import sys
import time

url = "http://localhost:8080"
client = InferenceClient(model=url)



# loading = True  # a simple var to keep the loading status
# loading_speed = 4  # number of characters to print out per second
# loading_string = "." * 6  # characters to print out one by one (6 dots in this example)
# while loading:
#     #  track both the current character and its index for easier backtracking later
#     for index, char in enumerate(loading_string):
#         # you can check your loading status here
#         # if the loading is done set `loading` to false and break
#         sys.stdout.write(char)  # write the next char to STDOUT
#         sys.stdout.flush()  # flush the output
#         time.sleep(1.0 / loading_speed)  # wait to match our speed
#     index += 1  # lists are zero indexed, we need to increase by one for the accurate count
#     # backtrack the written characters, overwrite them with space, backtrack again:
#     sys.stdout.write("\b" * index + " " * index + "\b" * index)
#     sys.stdout.flush()  # flush the output

prompt = "What is a deployment?"
output = client.text_generation(prompt, max_new_tokens=200, details=True)
print('Loading')
loading = True
while loading:
    time.sleep(.5)
    sys.stdout.write('.')
    sys.stdout.flush()
print(output.details.generated_tokens)
print(output.generated_text)

# gr.ChatInterface(
#     inference,
#     chatbot=gr.Chatbot(height=300),
#     textbox=gr.Textbox(placeholder="Chat with me!", container=False, scale=7),
#     description="This is the demo for a {model_name} model running on Google Kubernetes Engine".format(model_name=os.environ.get("MODEL_NAME")),
#     title="Open LLMs on Google Kubernetes Engine",
#     examples=["How do I deploy an Llama 2 to Kubernetes?"],
#     retry_btn="Retry",
#     undo_btn="Undo",
#     clear_btn="Clear",
# ).queue().launch()