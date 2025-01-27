# Install KServe with KNative and ISTIO

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-crds.yaml

kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-core.yaml

kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.16.0/istio.yaml

kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.16.0/net-istio.yaml

kubectl patch configmap/config-domain \
      --namespace knative-serving \
      --type merge \
      --patch '{"data":{"project.emlo":""}}'

kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-hpa.yaml

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml

kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve.yaml

kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve-cluster-resources.yaml

eksctl create iamserviceaccount \
	--cluster=canary-cluster \
	--name=s3-read-only \
	--attach-policy-arn=arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
	--override-existing-serviceaccounts \
	--region ap-south-1 \
	--approve

kubectl apply -f s3-secret.yaml

kubectl patch serviceaccount s3-read-only -p '{"secrets": [{"name": "s3-secret"}]}'

# Prometheus & Graphana

git clone --branch release-0.14 https://github.com/kserve/kserve.git

cd kserve 
kubectl apply -k docs/samples/metrics-and-monitoring/prometheus-operator
kubectl wait --for condition=established --timeout=120s crd/prometheuses.monitoring.coreos.com
kubectl wait --for condition=established --timeout=120s crd/servicemonitors.monitoring.coreos.com
kubectl apply -k docs/samples/metrics-and-monitoring/prometheus

kubectl patch configmaps -n knative-serving config-deployment --patch-file qpext_image_patch.yaml

kubectl create namespace grafana

helm repo add grafana https://grafana.github.io/helm-charts

helm install grafana grafana/grafana \
  --namespace grafana \
  --version 8.8.4 \
  --set readinessProbe.initialDelaySeconds=30 \
  --set readinessProbe.timeoutSeconds=5 \
  --set readinessProbe.httpGet.path=/api/health \
  --set readinessProbe.httpGet.port=3000

kubectl get secret --namespace grafana grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
password - bzjqhLGMRbCWXQb4CheNypbzIv71wlpGVB9VJMQP

export POD_NAME=$(kubectl get pods --namespace grafana -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")

kubectl --namespace grafana port-forward --address 0.0.0.0 $POD_NAME 3000
http://<EC2-IP>:3000
