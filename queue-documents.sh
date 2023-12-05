#!/bin/bash
while getopts f:t: flag
do
    case "${flag}" in
        f) filepath=${OPTARG};;
        t) topic=${OPTARG};;
    esac
done

echo "queuing documents for distributed processing..."
echo "---"
echo "File Path: $filepath";
echo "PubSub Topic: $topic";
echo "---"
# input="./data/k8s-urls.txt"
input="$filepath"
while IFS= read -r line
do
  echo "publishing $line"
  gcloud pubsub topics publish $topic --message="$line"
  # gcloud pubsub topics publish kubernetes_concepts-2 --message="$line"
done < "$input"