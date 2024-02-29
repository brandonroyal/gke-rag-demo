# Scaled Inference and RAG with Open LLMs
Llama-2 is a powerful open source language model that can be fine-tuned on your own custom dataset to perform a variety of tasks, such as text generation, translation, and summarization. Combined with Google Kubernetes (GKE), the most scalable Kubernetes platform for running large language models (LLMs) you can unlock the open source AI innovations with scalability, reliability, and ease of management.

## Demo Steps

1. Show GKE Console.  Show Llama 13B and Mistral 7B workloads

2. Show Llama 13B YAML and Mistral 7B YAML

3. Test a Prompt in the TGI UI

4. Walk through local [notebook](./notebook.ipynb)


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
# VERSION="1.28.3-gke.1203000"
VERSION="1.28.6-gke.1369000"
CHANNEL="rapid"
CLUSTER_NAME=l4-demo-1
gcloud container clusters create-auto $CLUSTER_NAME \
    --release-channel $CHANNEL --region $REGION \
    --cluster-version $VERSION
```

Authenticate
```bash
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION
```

Install Custom Metrics Adapter
```bash
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/deploy/production/adapter_new_resource_model.yaml
```

Create service account for to enable custom pubsub metrics
```bash
gcloud iam service-accounts create custom-metrics-viewer
```

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:custom-metrics-viewer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/monitoring.viewer"
```

```bash
gcloud iam service-accounts add-iam-policy-binding --role \
  roles/iam.workloadIdentityUser --member \
  "serviceAccount:$PROJECT_ID.svc.id.goog[custom-metrics/custom-metrics-stackdriver-adapter]" \
  custom-metrics-viewer@$PROJECT_ID.iam.gserviceaccount.com
```

Annotate custom metrics adapter service account with custom-metrics-viewer service account
```bash
kubectl annotate serviceaccount --namespace custom-metrics \
  custom-metrics-stackdriver-adapter \
  iam.gke.io/gcp-service-account=custom-metrics-viewer@$PROJECT_ID.iam.gserviceaccount.com
```

### Deploy Models using Text Generation Inference

Hugging Face requires authentication to download the [Llama-2-70b-chat-hf](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf) model, which means an access token is required to download the model.

You can get your access token from [huggingface.com > Settings > Access Tokens](https://huggingface.co/settings/tokens). Afterwards, set your HuggingFace token as an environment variable:
```bash
export HF_TOKEN=$(cat ./hf-token.txt)
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

### Create Cloud Pubsub Topic and Subscription for documents
```bash
gcloud pubsub topics create k8s_concepts
```

```bash
gcloud pubsub subscriptions create k8s_concepts_subscription --topic k8s_concepts
```

### Deploy Postgres, Indexer and Demo Chat App
Create service account to interact with pubsub topic
```bash
gcloud iam service-accounts create pubsub
```

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:pubsub@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/pubsub.editor"
```

Download service account key
```bash
gcloud iam service-accounts keys create ./.pubsub-svc/pubsub-svc.json \
    --iam-account=pubsub@$PROJECT_ID.iam.gserviceaccount.com
```

Create k8s secret from service account key
```bash
kubectl create secret generic pubsub-svc --from-file=./.pubsub-svc/pubsub-svc.json
```


Deploy Postgres with pgvector
```bash
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/indexer/
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


## Appendix

### Credits
* Sam Stoelinga