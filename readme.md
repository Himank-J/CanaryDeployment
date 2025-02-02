# Implementation of Canary Deployment using EKS, Torchscript and S3

This project demonstrates execution of canary deployment strategy for deployment of AI/ML models and the steps needed to achieve 100% rollout using this strategy. We will be making use of Elastic Kubernetes Service (EKS), Torchscript for creating model files and S3 for storing model files.

Contents - 
1. [What is Canary Deploment?](#what-is-canary-deployment)
2. [Why Canary Deployment is Needed for Production?](#why-canary-deployment-is-needed-for-production)
   
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


### Deployment & Monitoring Details


