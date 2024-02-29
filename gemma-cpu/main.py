from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from fastapi import FastAPI

tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b-it", token=os.environ["HF_TOKEN"])
model = AutoModelForCausalLM.from_pretrained("google/gemma-7b-it")

app = FastAPI()

def predict(input):
    

    input_text = "Write me a poem about Machine Learning."
    input_ids = tokenizer(input_text, return_tensors="pt")

    outputs = model.generate(**input_ids)
    return outputs

@app.get("/")
async def root():
    return predict("How many colors are there in the rainbow?")
