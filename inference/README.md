# Inference Demo


Stand-Up GKE Clusters
```bash
PROJECT_ID="broyal-llama-demo"
# create a cluster
gcloud container --project "$PROJECT_ID" clusters create-auto "autopilot-cluster-1" --region "us-central1" --release-channel "regular" --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/us-central1/subnetworks/default" --cluster-ipv4-cidr "/17" --services-ipv4-cidr "/22"

```

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