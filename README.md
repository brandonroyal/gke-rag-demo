# Inference Demo

## Demo 1 - Steps

*Goal*: Create an LLM inference API for a team of MLEs.  Make that API available horizontally scalable and secure using AI Infra on GKE.


1. View empty cluster and node pools in Pantheon. Inspect node configuration

2. Deploy llama-2 70b model
```bash
kubectl apply -f k8s/llama-2-70b/
```
```bash
kubectl describe deployment/llama-2-70b
```

3. Wait for deployment to become healthy from the console (3-4 mins to provision). Show logs to 
```bash
kubectl logs -l app=llama-2-70b -f
```

```bash
kubectl port-forward deployment/llama-2-70b 8080:8080
```

4. Run a quick test
```bash
curl 127.0.0.1:8080/generate -X POST \
    -H 'Content-Type: application/json' \
    --data-binary @- <<EOF
{
    "inputs": "[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n<</SYS>>\nHow to deploy a container on K8s?[/INST]",
    "parameters": {"max_new_tokens": 400}
}
EOF
```

5. Deploy llama-2 13B and Mistral 7B model for comparison.  Deploy services to expose the APIs
```bash
kubectl apply -f k8s/llama-2-13b k8s/mistral-7b
```

6. Compare the the models side by side in the browswer
```bash
kubectl apply -f k8s/llama-2-13b/service.yaml,k8s/llama-2-70b/service.yaml,k8s/mistral-7b/service.yaml 
```

7. Open the Services view in the console and open each of the load balanced services

*Llama 2* Prompt
```json
{
  "inputs": "[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. \
        Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. \
        If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.  Try to keep your response to 200 words or less.\n<</SYS>>\nWhat is a deployment?[/INST]",
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
*Mistral Prompt
```json
{
  "inputs": "[INST] You are a helpful, respectful and honest assistant who is an expert in explaining Kubernetes concepts. \
        Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. \
        If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Try to keep your response to 200 words or less. [/INST] {message}",
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

## Pre-Demo Steps

1. Choose your region and set your project:
```bash
export REGION=us-central1
export PROJECT_ID=$(gcloud config get project)
```

2. Create a GKE cluster:
```bash
gcloud container clusters create llm-demo-1 --location ${REGION} \
  --workload-pool ${PROJECT_ID}.svc.id.goog \
  --enable-image-streaming \
  --enable-ip-alias \
  --node-locations=$REGION-a \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --addons GcsFuseCsiDriver   \
  --no-enable-master-authorized-networks \
  --machine-type n2d-standard-4 \
  --num-nodes 1 --min-nodes 1 --max-nodes 5 \
  --ephemeral-storage-local-ssd=count=2 \
  --enable-ip-alias \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM,DAEMONSET,DEPLOYMENT,HPA,POD,STATEFULSET,STORAGE \
  --enable-managed-prometheus \
  --gateway-api=standard
```

3. Create a node pool
```bash
gcloud container node-pools create g2-standard-24 --cluster llm-demo-1 \
  --accelerator type=nvidia-l4,count=2,gpu-driver-version=latest \
  --machine-type g2-standard-24 \
  --ephemeral-storage-local-ssd=count=2 \
  --enable-autoscaling --enable-image-streaming \
  --num-nodes=0 --min-nodes=0 --max-nodes=3 \
  --node-locations $REGION-a,$REGION-b --region $REGION --spot 
```

4. Add role bindings for default GKE service account
```bash
gcloud projects get-iam-policy broyal-llama-demo  \
--flatten="bindings[].members" \
--format='table(bindings.role)' \
--filter="bindings.members:515586963527-compute@developer.gserviceaccount.com"
```

```bash
gcloud projects add-iam-policy-binding broyal-llama-demo \
    --member="serviceAccount:515586963527-compute@developer.gserviceaccount.com" \
    --role="roles/editor"
```

```bash
# needed for GKE ingress
gcloud projects add-iam-policy-binding broyal-llama-demo \
    --member="serviceAccount:515586963527-compute@developer.gserviceaccount.com" \
    --role="roles/compute.securityAdmin"
```


3. Deploy HF_TOKEN secret
```bash
source .env
kubectl create secret generic l4-demo --from-literal="HF_TOKEN=$HF_TOKEN"
```

## Appendix
test with curl:
```bash
curl 127.0.0.1:8080/generate -X POST \
    -H 'Content-Type: application/json' \
    --data-binary @- <<EOF
{
    "inputs": "[INST] <<SYS>>\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n<</SYS>>\nHow to deploy a container on K8s?[/INST]",
    "parameters": {"max_new_tokens": 400}
}
EOF
```

load testing 
```bash
./hey -n 2 -c 2 \
    -m "POST" -H "Content-Type: application/json" \
    -D ./test-prompt.json \
    -t 0 \
    http://localhost:8080/generate

```



Credits:
* text-generation-inference - huggingface
* text-generation-inference helm chart - louis030195