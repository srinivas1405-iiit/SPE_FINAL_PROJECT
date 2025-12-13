# Semantic Search Engine - DevOps Automation Framework
**CSE 816: Software Production Engineering Final Project**

This project implements a complete DevOps framework for a **Semantic Search Engine** application. It automates the Software Development Life Cycle (SDLC) using industry-standard tools for CI/CD, containerization, orchestration, and monitoring.

## 🚀 Project Overview

The core application is a Flask-based Search Engine that leverages **TensorFlow Hub (Universal Sentence Encoder)** to provide semantic similarity search capabilities, going beyond simple keyword matching.

The DevOps framework enables:
- **Continuous Integration**: Automated builds and testing via Jenkins.
- **Continuous Deployment**: Seamless deployment to Kubernetes using Ansible.
- **Scalability**: Horizontal Pod Autoscaling (HPA) based on CPU load.
- **Observability**: Centralized logging and visualization with the ELK Stack.
- **Security**: Infrastructure for secret management using HashiCorp Vault.

---

## 🛠️ Technology Stack

| Component | Tool(s) Used | Description |
| :--- | :--- | :--- |
| **Source Code** | Python, Flask, TensorFlow | REST API for Semantic Search. |
| **Version Control** | Git & GitHub | Source code management. |
| **CI/CD** | Jenkins | Automated pipeline for Build, Test, Push, and Deploy. |
| **Containerization** | Docker | Packaging application and dependencies. |
| **Orchestration** | Kubernetes (Minikube) | Managing containerized workloads. |
| **Config Mgmt** | Ansible | Automating Kubernetes manifest application using Roles. |
| **Monitoring** | ELK Stack | Elasticsearch, Logstash, Kibana for log aggregation. |


---

## ⚙️ Architecture & Pipeline

The project follows a robust pipeline flow:

1.  **Commit**: Developer pushes code to GitHub.
2.  **Trigger**: Jenkins detects changes (SCM Polling/Webhooks).
3.  **Build**: Jenkins builds the Docker image.
4.  **Test**: Automated `pytest` suite is executed.
5.  **Push**: Docker image is pushed to Docker Hub (`srinivas1405/semantic-search-engine`).
6.  **Deploy**: Ansible Playbook applies Kubernetes manifests to the cluster.
7.  **Monitor**: Logs are shipped to Logstash and visualized in Kibana.

---

## 🏃‍♂️ Getting Started

### Prerequisites
- **Minikube** installed and running.
- **Docker** installed.
- **Jenkins** deployed in the cluster (or external).

### Installation (Manual)

To deploy the entire stack manually (without Jenkins):

```bash
# 1. Apply Kubernetes Manifests
kubectl apply -f k8s/

# 2. Deploy Application via Ansible
cd semantic-search-engine-main/ansible
ansible-playbook deploy.yml
```

### Accessing the Application

| Service | access URL (Minikube) |
| :--- | :--- |
| **Search App** | `http://<minikube-ip>:30005` (NodePort) |
| **Kibana** | `http://<minikube-ip>:30601` (NodePort) |
| **Jenkins** | `http://<minikube-ip>:30000` (NodePort) |


*(Note: Check your specific Service NodePorts if different)*

---

## ✨ Key Features (Evaluation Criteria)

-   **✅ Modular Design**: Ansible code is structured into reusable Roles (`roles/k8s_deploy`).
-   **✅ Scalability**: Kubernetes HPA configured to auto-scale pods when CPU > 50%.
    -   *Verification*: `kubectl get hpa`
-   **✅ Live Patching**: Rolling Updates enabled in Deployments to ensure zero downtime.
-   **✅ Log Aggregation**: Application logs are automatically shipped to ELK.
    -   *Logstash Config*: Listens on TCP port 5000.
    -   *App Integration*: Uses `python-logstash` handler.
-   **✅ Domain Specific**: Implementation of **MLOps/AI-based Search** utilizing Vector Space Models.

---



## 🧪 Testing

Run unit tests locally:
```bash
cd semantic-search-engine-main
pip install -r requirements.txt
python -m pytest tests/
```
i am srinivas