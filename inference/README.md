# Inference Demo

## Steps

1. View empty cluster and node pools in Pantheon. Inspect node configuration

2. Deploy llama-2 text-generation-interface
```bash
kubectl apply -f text-generation-interface.yaml
```
```bash
kubectl describe deployment/llama-2-13b
```
3. Wait for deployment to become healthy (3-4 mins to provision). Port forward to do initial testing
```bash
kubectl describe deployment/llama-2-13b
```

```bash
kubectl port-forward deployment/llama-2-13b 8080:8080
```

4. 


Connect to Cluster
```bash
# get the kubeconfig
gcloud container clusters get-credentials autopilot-cluster-1 --region us-central1

# create a global static ip
gcloud compute addresses create text-generation-inference-ip --global

# create a A record in your domain pointing to the ip returned in this command
gcloud compute addresses describe text-generation-inference-ip --global

# deploy a model (default to bigscience/bloomz-7b1 on a100 gpu)
helm install text-generation-inference louis030195/text-generation-inference --set ingress.host=your.domain.com

# query the model
curl https://your.domain.com/bloomz-7b1 \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":17}}' \
    -H 'Content-Type: application/json'

```



Credits:
* text-generation-inference - huggingface
* text-generation-inference helm chart - louis030195