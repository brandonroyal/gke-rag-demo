# GenAI on GKE - Demo

## Demo Steps

1. Show GKE Console.  Nodepool w/ Autoscaling.  Show Llama 13B workloads

2. Show Llama 13B YAML and Mistral 7B YAML. Show healthchecks

3. Test a Prompt in the TGI UI

4. Walk through local 

## Pre-Demo Steps

### TGI
Preload the Prompts in the interface

Llama 2
```javascript
{
  "inputs": "[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.  Try to keep your response to 200 words or less.\n<</SYS>>\nWhat is a deployment?[/INST]",
  "parameters": {
    "best_of": 1,
    "do_sample": true,
    "max_new_tokens": 400,
    "repetition_penalty": 1.03,
    "return_full_text": false,
    "temperature": 0.5,
    "top_k": 10,
    "top_n_tokens": 5,
    "top_p": 0.95,
    "truncate": null,
    "typical_p": 0.95,
    "watermark": true
  }
}
```

Mistral
```javascript
{
  "inputs": "[INST] You are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.  Try to keep your response to 100 words or less. What is a deployment?[/INST]",
  "parameters": {
    "best_of": 1,
    "do_sample": true,
    "max_new_tokens": 400,
    "repetition_penalty": 1.03,
    "return_full_text": false,
    "temperature": 0.5,
    "top_k": 10,
    "top_n_tokens": 5,
    "top_p": 0.95,
    "truncate": null,
    "typical_p": 0.95,
    "watermark": true
  }
}
```

### Notebook
Ensure URL is resolving to the Mistral 7B NF4 service
```bash
ping mistral-7b.broyal.demo
```

Port forward postgres on dev machine
```bash
kubectl port-forward pod/postgres 5432:5432
```

### Chat App UI
Port forward `chat-app` on local machine
```bash
kubectl port-forward chat-app-bc9dd7f44-wjgg6 8080:7860
```

