# Implementation of Canary Deployment using EKS, Torchscript and S3

This project demonstrates execution of canary deployment strategy for deployment of AI/ML models and the steps needed to achieve 100% rollout using this strategy. We will be making use of Elastic Kubernetes Service (EKS), Torchscript for creating model files and S3 for storing model files.

Contents - 
1. [What is Canary Deploment?](#what-is-canary-deployment)
2. [Why Canary Deployment is Needed for Production?](#why-canary-deployment-is-needed-for-production)
3. [Key Components and Their Roles](#key-components-and-their-roles)
4. [Implementation Details](#implementation-details)
   
	4.1. [Code Details](#code-details)
   
   	4.2. [Deployment & Monitoring Details](#deployment-&-monitoring-details)
   
6. [Conclusion](#conclusion)
   
# What is Canary Deploment?

Canary deployment is a progressive rollout strategy used to deploy new software versions, including ML models, with minimal risk. It ensures that a small subset of users interacts with the new version before rolling it out to the entire user base.

## **Working -**

1. Baseline Model (Old Version) is Live

	- The existing model serves all traffic as the stable version.

2. Deploy New Model to a Small User Subset

	- A small percentage (e.g., 5-10%) of incoming traffic is routed to the new model (the “canary”).
	- Performance is closely monitored to detect issues (e.g., accuracy drop, latency increase).

3. Monitor Performance Metrics

	- Track key indicators such as accuracy, response time, error rate, and business impact (e.g., conversion rate).
	- Compare results with the old version to ensure improvements.

4. Gradual Traffic Increase

	- If the new model performs well, traffic allocation is increased (e.g., 25%, 50%, 100%) in controlled steps.
	- If issues arise, the deployment is rolled back without affecting most users.

5. Full Rollout or Rollback

	- If the new model is stable, it replaces the old model entirely.
	- If significant issues are found, traffic is reverted to the old model, ensuring minimal disruption.

## Why Canary Deployment is Needed for Production?

1. Risk Mitigation 🚨
	- Instead of exposing all users to a potentially faulty model, only a fraction of traffic experiences it.
	- If issues are detected, the rollout can be stopped or reversed before widespread impact.

2. Controlled Testing in a Live Environment 🧪
	- Unlike A/B testing (which is more experimental), canary deployment validates real-world performance while ensuring business continuity.
	- Helps in catching unexpected issues like model drift, bias, or infrastructure failures.

3. Faster Detection & Rollback 🔄
	- If the new model causes failures or degrades performance, it can be rolled back instantly.
	- No need to manually redeploy the old model, saving time and effort.

4. Avoids Full Downtime 🕒
	- Traditional full-rollout updates risk complete failure if something goes wrong.
	- Canary deployment keeps the old model running, ensuring continuous service availability.

5. Optimized for Cloud & Kubernetes ☁️
	- Modern cloud platforms (AWS, Azure, GCP) and Kubernetes support automated canary deployments.
	- Integration with CI/CD pipelines enables seamless model updates.

## Key Components and Their Roles

1. Amazon EKS (Elastic Kubernetes Service) - Provides a managed Kubernetes environment to host and orchestrate containerized applications, ensuring scalability, reliability, and ease of management.

2. eksctl - CLI tool for creating and managing EKS clusters.

3. Istio - Service mesh that provides traffic management, security, and observability for microservices.

4. KServe - Model serving platform for deploying and managing machine learning models on Kubernetes.

5. TorchScript - Converts PyTorch models into a format suitable for deployment.

6. Amazon S3 - Object storage service used to store the model weights.

7. Monitoring and Observability Tools -

 	- Prometheus - Monitoring and alerting toolkit for collecting and querying metrics.
  	- Grafana - Visualizes data through dashboards and graphs.
  
## Implementation Details - 

### Code Details

Step 1  - Creating handler file. We will use imagenet models only, hence we can create a common handler which will be applicable for all models used.
[classifier_handler.py](classifier-deployment/classifier_handler.py)

Step 2 - Download all required models. We will download 3 models:

- Hand gesture detection
- Age group detection
- Face emotion detection

[download_model.py](classifier-deployment/download_models.py)
```python
def get_processor_and_model(hf_string):
	processor = AutoImageProcessor.from_pretrained(hf_string, use_fast=True)
	model = AutoModelForImageClassification.from_pretrained(hf_string)

	return [processor, model]

def save_model_processor(model, processor, save_prefix_str):
	model.save_pretrained(f"./models/{save_prefix_str}/model")
	processor.save_pretrained(f"./models/{save_prefix_str}/processor")


[emotions_processor, emotions_model] = get_processor_and_model("dima806/facial_emotions_image_detection")
save_model_processor(emotions_model, emotions_processor, "emotions-classifier")
```

Step 3 - Now we need to convert each model to mar file. For this we will use torch-model-archiver

[create_mar.py](classifier-deployment/create_mar.py)
```python
def create_mar_file(model, model_store_dir):
    cmd = [
        "torch-model-archiver",
        "--model-name", model,
        "--handler", "classifier_handler.py",
        "--extra-files", f"models/{model}/",
        "--version", "1.0",
        "--export-path", model_store_dir,
    ]
    try:
        logger.info(f"Creating {model}.mar in {model_store_dir}")
        subprocess.check_call(cmd)
        logger.info(f"Created {model}.mar in {model_store_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create MAR file for {model}: {e}", exc_info=True)
```

Step 4 - Upload all files to S3

```bash
aws s3 cp --recursive model-store s3://<bucket-name>/<folder-name>/
```
During boostrap, our code will fetch model files from S3 and load it.

Now we are done with code implemenbtation, we will proceed with deployments.

### Deployment & Monitoring Details

Flow - We will follow below flow for rollout using canary deployment
1. Deployment of emotion detection model with 100% volume
2. Deployment of Age group detection model with 30% volume
3. Deployment of Age group detection model with 100% volume and 2 replicas
4. Deployment of Hand gesture detection model with 30% volume
5. Deployment of Hand gesture detection model with 100% volume and 2 replicas
   
Step 1 - Deployment of emotion detection model with 100% volume - [classifier-vit-1.yaml](classifier-deployment/deployment/classifier-vit-1.yaml)
```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "classifier-vit"
  annotations:
    serving.kserve.io/enable-metric-aggregation: "true"
    serving.kserve.io/enable-prometheus-scraping: "true"
    autoscaling.knative.dev/target: "1"
spec:
  predictor:
    minReplicas: 0
    maxReplicas: 3
    containerConcurrency: 3
    # canaryTrafficPercent: 100
    serviceAccountName: s3-read-only
    pytorch:
      protocolVersion: v1
      storageUri: s3://canary-models-vit/kserve/emotions-classifier/
      image: pytorch/torchserve-kfs:0.12.0
      resources:
        limits:
          cpu: 2000m
          memory: 4Gi
      env:
        - name: TS_DISABLE_TOKEN_AUTHORIZATION
          value: "true"
```
Here we have provided the S3 path of emotions-classifier as storageUri

```bash
kubectl apply -f classifier-vit-1.yaml
```

**Check Status**

<img width="700" alt="Screenshot 2025-02-01 at 5 52 36 PM" src="https://github.com/user-attachments/assets/dd17068e-0d66-42ca-862c-34aa0375b675" />

**Load test**

<img width="700" alt="Screenshot 2025-02-01 at 6 03 39 PM" src="https://github.com/user-attachments/assets/1f55a468-c53d-4ff7-b70e-a8dee61c7df8" />

**Service Latency**

<img width="700" alt="Screenshot 2025-02-01 at 6 03 54 PM" src="https://github.com/user-attachments/assets/12949f41-23db-4bb3-9bfa-0088fcb23084" />

**Service Request Volume & Response Time by Revision**

<img width="700" alt="Screenshot 2025-02-01 at 6 04 03 PM" src="https://github.com/user-attachments/assets/26e40f28-0f4b-464a-8b9f-6f0674ffcd6b" />

Step 2 - Deployment of Age group detection model with 30% volume - [classifier-vit-2.yaml](classifier-deployment/deployment/classifier-vit-2.yaml)
```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "classifier-vit"
  annotations:
    serving.kserve.io/enable-metric-aggregation: "true"
    serving.kserve.io/enable-prometheus-scraping: "true"
    autoscaling.knative.dev/target: "1"
spec:
  predictor:
    minReplicas: 0
    maxReplicas: 3
    containerConcurrency: 3
    canaryTrafficPercent: 30
    serviceAccountName: s3-read-only
    pytorch:
      protocolVersion: v1
      storageUri: s3://canary-models-vit/kserve/faces-age-detection/
      image: pytorch/torchserve-kfs:0.12.0
      resources:
        limits:
          cpu: 2000m
          memory: 4Gi
      env:
        - name: TS_DISABLE_TOKEN_AUTHORIZATION
          value: "true"
```

**Check status**

<img width="700" alt="Screenshot 2025-02-01 at 6 08 00 PM" src="https://github.com/user-attachments/assets/856be15c-ee0a-4660-8921-e40e0a343aa7" />

As we can see now 30% volume is shifted towards latest deployment

**Pods Status**

<img width="700" alt="Screenshot 2025-02-01 at 6 09 56 PM" src="https://github.com/user-attachments/assets/2d117303-3d78-4187-a050-39484b3acc46" />

Few pods related to deployment 1 are terminating and new pods related to deployment are spinning up to serve 30% volume.

**Service Latency**

<img width="700" alt="Screenshot 2025-02-01 at 6 11 31 PM" src="https://github.com/user-attachments/assets/50ffed11-72e7-4976-b078-ae36787fd8d1" />

**Service Request Volume & Response Time by Revision**

<img width="700" alt="Screenshot 2025-02-01 at 6 11 41 PM" src="https://github.com/user-attachments/assets/05c10823-c12d-4901-8cb7-6c7b5127bf60" />


Step 3 - Deployment of Age group detection model with 100% volume - [classifier-vit-2.yaml](classifier-deployment/deployment/classifier-vit-2.yaml)

  - Just switch `canaryTrafficPercent` to 100 and deploy

**Check Status**

<img width="700" alt="Screenshot 2025-02-01 at 6 14 42 PM" src="https://github.com/user-attachments/assets/25681779-4fc6-4207-995c-6af45b5fb057" />

A version 3 is deployed which now serves 100% of the requests

**Service Latency**

<img width="700" alt="Screenshot 2025-02-01 at 6 23 19 PM" src="https://github.com/user-attachments/assets/3e49b2d1-dd1e-4dd6-ba35-7bd135c03c54" />

**Service Request Volume & Response Time by Revision**

<img width="700" alt="Screenshot 2025-02-01 at 6 23 29 PM" src="https://github.com/user-attachments/assets/cb3e858e-343b-4a49-8181-bac2cbbbd058" />

Step 4 - Deployment of Hand gesture detection model with 30% volume - [classifier-vit-3.yaml](classifier-deployment/deployment/classifier-vit-3.yaml)

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "classifier-vit"
  annotations:
    serving.kserve.io/enable-metric-aggregation: "true"
    serving.kserve.io/enable-prometheus-scraping: "true"
    autoscaling.knative.dev/target: "1"
spec:
  predictor:
    minReplicas: 2
    maxReplicas: 3
    containerConcurrency: 3
    canaryTrafficPercent: 30
    serviceAccountName: s3-read-only
    pytorch:
      protocolVersion: v1
      storageUri: s3://canary-models-vit/kserve/hand-gestures-classifier/
      image: pytorch/torchserve-kfs:0.12.0
      resources:
        limits:
          cpu: 2000m
          memory: 4Gi
      env:
        - name: TS_DISABLE_TOKEN_AUTHORIZATION
          value: "true"
```
Again we have modified the `storageUri` to hand gesture classifier

**Check status**

<img width="700" alt="Screenshot 2025-02-01 at 6 26 22 PM" src="https://github.com/user-attachments/assets/25809e52-cc6f-4d11-9751-c5b43bc619a8" />

30% shifted to deployment 4

Step 5 - Deployment of Hand gesture detection model with 100% volume and 2 replicas - [classifier-vit-3.yaml](classifier-deployment/deployment/classifier-vit-3.yaml)
  - Just switch `canaryTrafficPercent` to 100 and deploy

**Check status**

<img width="1052" alt="Screenshot 2025-02-01 at 6 31 51 PM" src="https://github.com/user-attachments/assets/b7e78734-6e9b-4595-8d34-19d81a26c4f3" />

Finally all trafic has shifted to Hand gesture classifier

**Service Latency**

<img width="1438" alt="Screenshot 2025-02-01 at 6 37 12 PM" src="https://github.com/user-attachments/assets/90087e29-92f1-4fed-9df4-1ce08bd29f3e" />

**Service Request Volume & Response Time by Revision**

<img width="1437" alt="Screenshot 2025-02-01 at 6 37 20 PM" src="https://github.com/user-attachments/assets/0c301a6c-11ec-441e-956e-390af3eca287" />

## Conclusion

- We learnt important of canary deployments
- Implemented traffic management between 3 models:
	- we started with 100% traffic to 1st model
 	- 30% traffic to 2nd model followed by promotion to 100% traffic
  	- 30% traffic to 3rd model followed by promotion to 100% traffic
 
- Used prometheus and grafana by metrics tracking
