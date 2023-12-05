kubectl apply -f ./k8s/indexer-job
# kubectl describe job/indexer-job
echo "---"
echo "waiting for job to start..."
sleep 3s
# kubectl get job/indexer-job -ojson | jq ".status.active"
kubectl logs job/indexer-job --all-containers=true -f
# kubectl logs -l job=indexer -f
# kubectl get job/indexer-job -ojson | jq ".status.active"
# while [ $(kubectl get job/indexer-job -ojson | jq ".status.active") -le 1 ]
# do
   
# done
# kubectl get jobs -l job-name=indexer-job
# echo "---"
# echo "waiting for job to start..."
# kubectl wait --for=condition=Ready job/indexer-job --timeout=300s && kubectl logs -l job-name=indexer-job