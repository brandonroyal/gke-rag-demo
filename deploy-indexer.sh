kubectl apply -f ./k8s/indexer-job
kubectl describe job/indexer-job
kubectl get jobs -l job-name=indexer-job
echo "---"
# echo "logs job-name=indexer-job"
# echo "126 chunks in 4 pages"
# echo "connectingn to vectordb. adding documents to kubernetes_concepts..."
kubectl logs -l job-name=indexer-job