# Inference Demo

## Demo 1 - Steps

*Goal*: Create an LLM inference API for a team of MLEs.  Make that API available horizontally scalable and secure using AI Infra on GKE.


1. View empty cluster and node pools in Pantheon. Inspect node configuration

2. Deploy llama-2 70b model
```bash
kubectl apply -f llama-2-70b.yaml
```
```bash
kubectl describe deployment/llama-2-7b
```
3. Wait for deployment to become healthy (3-4 mins to provision). Port forward to do initial testing
```bash
kubectl describe deployment/llama-2-13b
```

```bash
kubectl port-forward deployment/llama-2-13b 8080:8080
```

4. 


## Pre-Demo Steps

1. Choose your region and set your project:
```bash
export REGION=us-central1
export PROJECT_ID=$(gcloud config get project)
```

2. Create a GKE cluster:
```bash
gcloud container clusters create l4-demo --location ${REGION} \
  --workload-pool ${PROJECT_ID}.svc.id.goog \
  --enable-image-streaming --enable-shielded-nodes \
  --shielded-secure-boot --shielded-integrity-monitoring \
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
  --enable-managed-prometheus
```

3. Create a node pool
```bash
--logging=SYSTEM,WORKLOAD
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