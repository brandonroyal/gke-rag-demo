# Scaled Inference and RAG with Open LLMs
Llama-2 is a powerful open source language model that can be fine-tuned on your own custom dataset to perform a variety of tasks, such as text generation, translation, and summarization. Combined with Google Kubernetes (GKE), the most scalable Kubernetes platform for running large language models (LLMs) you can unlock the open source AI innovations with scalability, reliability, and ease of management.

## Test in Swagger Inferface





## Demo Setup

### Prerequisites
* A terminal with `kubectl` and `gcloud` installed.
* GCP Project with GPU quota to run 2 L4 GPUs
* Enabled Org Policies
* Request access to Meta Llama models by submitting the [request access form](https://ai.meta.com/resources/models-and-libraries/llama-downloads/)
* Agree to the Llama 2 terms on the [Llama 2 70B Chat HF](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf) model in HuggingFace

### Create GKE Cluster

Choose your region and set your project:
```bash
export REGION=us-central1
export PROJECT_ID=$(gcloud config get project)
```

Create a GKE Autopilot cluster:
```bash
VERSION="1.28.3-gke.1203000"
CHANNEL="rapid"
CLUSTER_NAME=l4-demo
gcloud container clusters create-auto $CLUSTER_NAME \
    --release-channel $CHANNEL --region $REGION \
    --cluster-version $VERSION
```

<!-- Create and connect to VPC peering for AlloyDB in default VPC
```bash
gcloud compute addresses create google-managed-services-default \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --description="peering range for Google" \
    --network=default
```

```bash
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=google-managed-services-default \
    --network=default
```

Create AlloyDB cluster:
```bash
gcloud alloydb clusters create db-cluster \
    --password=$DB_PASSWORD \
    --network=default \
    --region=$REGION \
    --project=$PROJECT_ID \
    --allocated-ip-range-name=google-managed-services-default
```

Create AlloyDB instance:
```bash
gcloud alloydb instances create vector-db \
    --instance-type=PRIMARY \
    --cpu-count=2 \
    --region=$REGION \
    --cluster=db-cluster \
    --project=$PROJECT_ID
```

Get the AlloyDB instance IP
```bash
gcloud alloydb instances describe vector-db \
 --region=$REGION \
 --cluster=db-cluster \
 --project=$PROJECT_ID
``` -->

### Deploy Models using Text Generation Inference

Hugging Face requires authentication to download the [Llama-2-70b-chat-hf](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf) model, which means an access token is required to download the model.

You can get your access token from [huggingface.com > Settings > Access Tokens](https://huggingface.co/settings/tokens). Afterwards, set your HuggingFace token as an environment variable:
```bash
export HF_TOKEN=<paste-your-own-token>
```

Create a Secret to store your HuggingFace token which will be used by the K8s job:
```bash
kubectl create secret generic l4-demo --from-literal="HF_TOKEN=$HF_TOKEN"
```

Deploy llama-2-13b on TGI:
```bash
kubectl apply -f k8s/llama-2-13b/
```

Deploy mistral-7b on TGI
```bash
kubectl apply -f k8s/mistral-7b/
```

Wait for Node Pool instances to be provisioned and successful scheduling of llama-2-13b and mistral-7b
```bash
kubectl events
```

Watch logs and wait for server to successfully start
```bash
kubectl logs -l app=llama-2-13b
```

```bash
kubectl logs -l app=mistral-7b
```

Get URL and browse of the llama 2 and mistral APIs
```bash
echo -n "http://$(kubectl get service llama-2-13b-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/docs"
```

```bash
echo -n "http://$(kubectl get service mistral-7b-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/docs"
```

Test with a prompt

llama-2-13b
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

mistral-7b
```javascript
{
  "inputs": "[INST]  You are a garden who has been trained to provide helpful, respectful and honest answers about yourself and garden plants. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.  Try to keep your response to 100 words or less. When should I plant asparagus?[/INST]",
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

### Deploy Postgres and Demo Chat App
Deploy Postgres with pgvector
```bash
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/chat-app/
```

Wait for NodePool to be ready and pod to be scheduled successfully
```bash
kubectl events -w
```

Confirm postgres is health and ready to recieve connections
```bash
kubectl logs pod/postgres
```

In a separate tab, proxy the connection to postgres
```bash
kubectl port-forward postgres 5432:5432
```

### Load grounded data into Cloud Pubsub
```bash
gcloud pubsub
```

### 
```bash
kubectl create secret generic pubsub-svc --from-file=./.pubsub-svc/pubsub-svc.json
```


## Appendix

### Credits
* Sam Stolinga (sp?)