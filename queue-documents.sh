#!/bin/bash
echo "queuing documents for distributed processing..."
echo "---"
input="./data/k8s-urls.txt"
while IFS= read -r line
do
  echo "publishing $line"
  gcloud pubsub topics publish kubernetes_concepts --message="$line"
done < "$input"