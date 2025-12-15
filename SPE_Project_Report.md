# CSE 816: Software Production Engineering
# Final Project Report

---

## Project Title: Semantic Search Engine - DevOps Automation Framework

**Submitted by:** Srinivas, Kireeti  
**Roll Numbers:** IMT2022066, IMT2022059  
**Date:** December 12, 2025

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Implementation Details](#4-implementation-details)
   - 4.1 [Version Control (Git & GitHub)](#41-version-control-git--github)
   - 4.2 [Containerization (Docker)](#42-containerization-docker)
   - 4.3 [CI/CD Pipeline (Jenkins)](#43-cicd-pipeline-jenkins)
   - 4.4 [Configuration Management (Ansible)](#44-configuration-management-ansible)
   - 4.5 [Orchestration (Kubernetes)](#45-orchestration-kubernetes)
   - 4.6 [Monitoring & Logging (ELK Stack)](#46-monitoring--logging-elk-stack)
5. [Advanced Features](#5-advanced-features)
   - 5.1 [HashiCorp Vault](#51-hashicorp-vault)
   - 5.2 [Ansible Roles](#52-ansible-roles)
   - 5.3 [Horizontal Pod Autoscaler (HPA)](#53-horizontal-pod-autoscaler-hpa)
6. [Domain-Specific Implementation (MLOps/AIOps)](#6-domain-specific-implementation-mlopsaiops)
7. [Screenshots & Demonstration](#7-screenshots--demonstration)
8. [Pipeline Workflow](#8-pipeline-workflow)
9. [Challenges & Solutions](#9-challenges--solutions)
10. [Conclusion](#10-conclusion)
11. [References](#11-references)

---



## 1. Introduction

### 1.1 Problem Statement

Modern software development requires rapid, reliable, and repeatable deployment processes. Manual deployments are error-prone, time-consuming, and do not scale well. This project addresses these challenges by implementing a complete DevOps framework that:

1. Automates code build and testing upon every Git commit
2. Packages applications as portable Docker containers
3. Orchestrates deployments using Kubernetes for scalability
4. Provides centralized logging and monitoring for observability

### 1.2 Project Scope

The project implements a **Semantic Search Engine** that answers programming questions using TensorFlow's Universal Sentence Encoder for vector-based similarity search. The DevOps framework wraps this application with:

- Continuous Integration/Continuous Deployment (CI/CD)
- Container orchestration with auto-scaling
- Centralized log aggregation and visualization
- Infrastructure as Code (IaC) principles

---

## 2. Technology Stack

| Category | Tool(s) Used | Purpose |
|:---------|:-------------|:--------|
| **Application** | Python, Flask, TensorFlow Hub | REST API for semantic search |
| **Version Control** | Git & GitHub | Source code management |
| **CI/CD** | Jenkins with GitHub Webhooks | Automated build, test, push, deploy |
| **Containerization** | Docker, Docker Compose | Application packaging |
| **Container Registry** | Docker Hub | Image distribution |
| **Orchestration** | Kubernetes (Minikube) | Container orchestration |
| **Config Management** | Ansible with Roles | Infrastructure automation |
| **Secrets Management** | HashiCorp Vault | Secure credential storage |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | Log aggregation & visualization |

---

## 3. System Architecture

### 3.1 Data Flow

1. **Developer commits code** to GitHub repository
2. **GitHub webhook triggers** Jenkins pipeline
3. **Jenkins executes** the 4-stage pipeline (Build → Test → Push → Deploy)
4. **Docker image** is built, tested, and pushed to Docker Hub
5. **Ansible playbook** applies Kubernetes manifests to the cluster
6. **Application logs** are shipped to ELK Stack via Logstash
7. **Kibana dashboard** visualizes application logs and metrics

---

## 4. Implementation Details

### 4.1 Version Control (Git & GitHub)

The project uses Git for version control with GitHub as the remote repository. The repository structure:

```
SPE_FINAL_PROJECT/
├── k8s/                          # Kubernetes manifests
│   ├── elasticsearch-deployment.yaml
│   ├── elasticsearch-service.yaml
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── hpa.yaml                  # Horizontal Pod Autoscaler
│   ├── kibana-deployment.yaml
│   ├── logstash-config.yaml
│   ├── logstash-deployment.yaml
│   └── vault.yaml                # HashiCorp Vault
├── semantic-search-engine-main/
│   ├── ansible/
│   │   ├── deploy.yml
│   │   └── roles/
│   │       └── k8s_deploy/       # Ansible Role
│   ├── Dockerfile
│   ├── Jenkinsfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── SearchEngine_QA/          # Application code
└── Screenshots SPE/              # Project screenshots
```

**GitHub Integration:**
- Repository: `srinivas1405/SPE_FINAL_PROJECT`
- WebHooks configured for Jenkins SCM polling
- Branch protection and commit history maintained

---

### 4.2 Containerization (Docker)

#### 4.2.1 Dockerfile

The application is containerized using a multi-stage approach optimized for TensorFlow model caching:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install system dependencies and upgrade pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Preload the model during build time (Cache this layer!)
COPY preload_model.py .
RUN python preload_model.py

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the Flask app
CMD ["python", "SearchEngine_QA/searchES_FlaskAPI.py"]
```

**Key Optimization:** The TensorFlow Universal Sentence Encoder model is preloaded during the Docker build phase, ensuring this 1GB+ model is cached in a Docker layer, significantly reducing container startup time.

#### 4.2.2 Docker Compose (Local Development)

```yaml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.17.9
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    networks:
      - search-net

  web:
    build: .
    container_name: python-search-app
    ports:
      - "5000:5000"
    environment:
      - ELASTICSEARCH_HOST=elasticsearch
    depends_on:
      - elasticsearch
    networks:
      - search-net

networks:
  search-net:
    driver: bridge
```

---

### 4.3 CI/CD Pipeline (Jenkins)

The Jenkins pipeline implements a complete CI/CD workflow with 4 stages:

#### 4.3.1 Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'srinivas1405/semantic-search-engine'
        DOCKER_TAG = "v${BUILD_NUMBER}"
        KUBECONFIG = credentials('kubeconfig') 
    }

    stages {
        stage('Build') {
            steps {
                script {
                    dir('semantic-search-engine-main') {
                        echo 'Building Docker Image...'
                        sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                        sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo 'Running Tests...'
                    sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python -m pytest tests/"
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    echo 'Pushing payload to Docker Hub...'
                    docker.withRegistry('', 'docker-hub-credentials') {
                        dir('semantic-search-engine-main') {
                            sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh "docker push ${DOCKER_IMAGE}:latest"
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying to Kubernetes using Ansible...'
                    sh 'pip3 install kubernetes --break-system-packages'
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        dir('semantic-search-engine-main/ansible') {
                            sh 'export K8S_AUTH_KUBECONFIG=$KUBECONFIG && ansible-playbook deploy.yml'
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}
```

#### 4.3.2 Pipeline Stages Explained

| Stage | Description | Tools Used |
|:------|:------------|:-----------|
| **Build** | Builds Docker image with version tag | Docker |
| **Test** | Runs pytest inside container | pytest, Docker |
| **Push** | Pushes image to Docker Hub | Docker Hub |
| **Deploy** | Applies K8s manifests via Ansible | Ansible, kubectl |

---

### 4.4 Configuration Management (Ansible)

Ansible is used for automated deployment to Kubernetes with a modular role-based structure.

#### 4.4.1 Ansible Playbook (`deploy.yml`)

```yaml
---
- name: Deploy Application and Infrastructure to Kubernetes
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - k8s_deploy
```

#### 4.4.2 Ansible Role (`roles/k8s_deploy/tasks/main.yml`)

```yaml
---
- name: Apply Vault Manifest
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/vault.yaml

- name: Apply Elasticsearch Deployment
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/elasticsearch-deployment.yaml

- name: Apply Elasticsearch Service
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/elasticsearch-service.yaml

- name: Apply Logstash ConfigMap
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/logstash-config.yaml

- name: Apply Logstash Deployment
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/logstash-deployment.yaml

- name: Apply Kibana Deployment and Service
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/kibana-deployment.yaml

- name: Apply Flask App Deployment
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/flask-deployment.yaml

- name: Apply Flask App Service
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/flask-service.yaml

- name: Apply HPA
  kubernetes.core.k8s:
    state: present
    src: ../../k8s/hpa.yaml
```

---

### 4.5 Orchestration (Kubernetes)

The application runs on a Kubernetes cluster (Minikube) with the following components:

#### 4.5.1 Flask Application Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-search-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-search-app
  template:
    metadata:
      labels:
        app: python-search-app
    spec:
      containers:
      - name: python-search-app
        image: srinivas1405/semantic-search-engine:latest
        ports:
        - containerPort: 5000
        env:
        - name: ELASTICSEARCH_HOST
          value: "elasticsearch"
        resources:
          requests:
            cpu: "200m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "3Gi"
```

#### 4.5.2 Service Ports

| Service | Port | NodePort | Purpose |
|:--------|:----:|:--------:|:--------|
| Flask App | 5000 | 30005 | Main application |
| Kibana | 5601 | 30601 | Log visualization |
| Jenkins | 8080 | 30000 | CI/CD dashboard |
| Elasticsearch | 9200 | - | Log storage |
| Logstash | 5000 | - | Log ingestion |
| Vault | 8200 | - | Secrets management |

---

### 4.6 Monitoring & Logging (ELK Stack)

The ELK Stack provides centralized log aggregation and visualization.

#### 4.6.1 Logstash Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
data:
  logstash.conf: |
    input {
      tcp {
        port => 5000
        codec => json
      }
    }
    output {
      elasticsearch {
        hosts => ["elasticsearch:9200"]
        index => "app-logs-%{+YYYY.MM.dd}"
      }
      stdout { codec => rubydebug }
    }
```

#### 4.6.2 Application Integration

The Flask application integrates with Logstash using `python-logstash`:

```python
import logging
import logstash

# Configure Logging
host = 'logstash'
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

# Usage in API endpoint
@app.route('/api/search/<query>')
def search_api(query):
    test_logger.info('Search Query Received: ' + query)
    # ... search logic
```

---

## 5. Advanced Features

### 5.1 HashiCorp Vault

Vault is deployed for secure secrets management:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: vault
        image: vault:1.13.3
        args: ["server", "-dev", "-dev-listen-address=0.0.0.0:8200"]
        ports:
        - containerPort: 8200
        securityContext:
          capabilities:
            add: ["IPC_LOCK"]
```

**Use Cases:**
- Docker Hub credentials storage
- Kubernetes secrets management
- API keys for external services

---

### 5.2 Ansible Roles

The project implements modular Ansible code using roles:

```
ansible/
├── deploy.yml          # Main playbook
└── roles/
    └── k8s_deploy/     # Reusable role
        └── tasks/
            └── main.yml
```

**Benefits:**
- **Reusability:** Role can be used across different playbooks
- **Maintainability:** Separation of concerns
- **Scalability:** Easy to add new roles for different components

---

### 5.3 Horizontal Pod Autoscaler (HPA)

HPA is configured for dynamic scaling based on CPU utilization:

```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: python-search-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-search-app
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 50
```

**Configuration:**
- **Minimum Replicas:** 1
- **Maximum Replicas:** 5
- **Scale Trigger:** CPU > 50%

**Verification Command:**
```bash
kubectl get hpa
```

---

## 6. Domain-Specific Implementation (MLOps/AIOps)

### 6.1 Semantic Search with TensorFlow

Unlike typical web applications, this project implements a **domain-specific MLOps solution** for intelligent search:

#### 6.1.1 Vector Space Model

The application uses TensorFlow Hub's **Universal Sentence Encoder** to convert text into 512-dimensional embeddings:

```python
import tensorflow_hub as hub

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def sentenceSimilaritybyNN(es, sent):
    query_vector = tf.make_ndarray(tf.make_tensor_proto(embed([sent]))).tolist()[0]
    b = {
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }
    return es.search(index='questions-index', body=b)
```

#### 6.1.2 Dual Search Approach

| Search Type | Method | Use Case |
|:------------|:-------|:---------|
| **Keyword** | Elasticsearch `match` query | Exact term matching |
| **Semantic** | Cosine similarity on embeddings | Meaning-based search |

### 6.2 MLOps Characteristics

| Characteristic | Implementation |
|:---------------|:---------------|
| ML Model Integration | TensorFlow Universal Sentence Encoder |
| Model Caching | Docker layer caching during build |
| Vector Database | Elasticsearch with dense_vector type |
| Inference Pipeline | Real-time embedding generation |

---

## 7. Screenshots & Demonstration

### 7.1 Jenkins Pipeline

![Jenkins Pipeline Execution](Screenshots%20SPE/IMG-20251212-WA0003.jpg)
*Jenkins CI/CD Pipeline showing Build, Test, Push, and Deploy stages*

### 7.2 Jenkins Build Console

![Jenkins Console Output](Screenshots%20SPE/IMG-20251212-WA0004.jpg)
*Console output showing successful pipeline execution*

### 7.3 Docker Hub Repository

![Docker Hub](Screenshots%20SPE/IMG-20251212-WA0005.jpg)
*Docker images pushed to Docker Hub repository*

### 7.4 Kubernetes Pods

![Kubernetes Pods](Screenshots%20SPE/IMG-20251212-WA0006.jpg)
*Running pods in Kubernetes cluster showing all services*

### 7.5 Search Application UI

![Application UI](Screenshots%20SPE/IMG-20251212-WA0007.jpg)
*Semantic Search Engine web interface*

### 7.6 Search Results

![Search Results](Screenshots%20SPE/IMG-20251212-WA0008.jpg)
*Search results showing keyword and semantic matches*

### 7.7 Kibana Dashboard

![Kibana Logs](Screenshots%20SPE/IMG-20251212-WA0009.jpg)
*Kibana dashboard showing application logs*

### 7.8 Log Details

![Log Analysis](Screenshots%20SPE/IMG-20251212-WA0010.jpg)
*Detailed log analysis in Kibana*

### 7.9 HPA Status

![HPA Status](Screenshots%20SPE/IMG-20251212-WA0011.jpg)
*Horizontal Pod Autoscaler status*

### 7.10 Elasticsearch Index

![Elasticsearch](Screenshots%20SPE/IMG-20251212-WA0012.jpg)
*Elasticsearch index with log data*

### 7.11 Vault Dashboard

![Vault](Screenshots%20SPE/IMG-20251212-WA0013.jpg)
*HashiCorp Vault secrets management*

### 7.12 Complete System Overview

![System Overview](Screenshots%20SPE/IMG-20251212-WA0014.jpg)
*Complete system running with all components*

### 7.13 Kibana Dashboard - Log Visualization

![Kibana Dashboard Logs](Screenshots%20SPE/kibana%20dashboard%20to%20see%20logs.jpg)
*Kibana dashboard displaying application logs and search queries*

### 7.14 Semantic Search Engine with Results

![Semantic Search Results](Screenshots%20SPE/semantic%20search%20engine%20with%20results.jpg)
*Semantic Search Engine interface showing search results with semantic matching*

### 7.15 Additional System Screenshot

![Additional System View](Screenshots%20SPE/WhatsApp%20Image%202025-12-13%20at%2023.26.56_a0cc30b1.jpg)
*Additional view of the deployed system*

---

## 8. Pipeline Workflow

### 8.1 End-to-End Workflow

```mermaid
flowchart LR
    A[Developer Commit] --> B[GitHub Webhook]
    B --> C[Jenkins Trigger]
    C --> D[Build Stage]
    D --> E[Test Stage]
    E --> F[Push to Docker Hub]
    F --> G[Ansible Deploy]
    G --> H[Kubernetes Update]
    H --> I[Application Live]
    I --> J[Logs to ELK]
    J --> K[Kibana Dashboard]
```

### 8.2 Automated Triggers

| Trigger | Action |
|:--------|:-------|
| Git Push | Webhook triggers Jenkins |
| Jenkins Build Success | Docker image pushed |
| Docker Push Success | Ansible deployment starts |
| Deployment Complete | Application live with new changes |

---

## 9. Challenges & Solutions

### 9.1 TensorFlow Model Size

**Challenge:** Universal Sentence Encoder is ~1GB, causing slow container startup.

**Solution:** Implemented model preloading during Docker build phase:
```dockerfile
COPY preload_model.py .
RUN python preload_model.py
```

### 9.2 Kubernetes RBAC

**Challenge:** Jenkins pod couldn't access Kubernetes API.

**Solution:** Configured kubeconfig credentials in Jenkins and set `K8S_AUTH_KUBECONFIG` environment variable.

### 9.3 Elasticsearch Connection Retry

**Challenge:** Application crashed if Elasticsearch wasn't ready.

**Solution:** Implemented retry logic with exponential backoff:
```python
for i in range(30):
    try:
        es = Elasticsearch([{'host': es_host, 'port': 9200}])
        if es.ping():
            return es
    except Exception:
        pass
    time.sleep(2)
```

### 9.4 Log Shipping

**Challenge:** Logs weren't reaching Elasticsearch.

**Solution:** Used TCP handler instead of UDP for reliable log delivery:
```python
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))
```

---

## 10. Conclusion

This project successfully demonstrates a complete DevOps automation framework for a domain-specific MLOps application. The implementation includes:

### 10.1 Core Requirements Met

| Requirement | Implementation |
|:------------|:---------------|
| Version Control | Git + GitHub |
| CI/CD Pipeline | Jenkins with 4 stages |
| Containerization | Docker + Docker Compose |
| Configuration Management | Ansible with Roles |
| Orchestration | Kubernetes (Minikube) |
| Monitoring/Logging | ELK Stack |

### 10.2 Advanced Features

| Feature | Implementation |
|:--------|:---------------|
| Vault | HashiCorp Vault |
| Ansible Roles | Modular k8s_deploy role |
| Kubernetes HPA | Auto-scaling 1-5 pods |

### 10.3 Domain-Specific Value

| Aspect | Value |
|:-------|:------|
| Domain | MLOps/AIOps |
| ML Model | TensorFlow Universal Sentence Encoder |
| Innovation | Dual search (Keyword + Semantic) |


---

## 11. References

1. Jenkins Documentation: https://www.jenkins.io/doc/
2. Kubernetes Documentation: https://kubernetes.io/docs/
3. Docker Documentation: https://docs.docker.com/
4. Ansible Documentation: https://docs.ansible.com/
5. Elasticsearch Documentation: https://www.elastic.co/guide/
6. TensorFlow Hub: https://tfhub.dev/google/universal-sentence-encoder/4
7. HashiCorp Vault: https://www.vaultproject.io/docs

---

## Appendix A: Access URLs

| Service | URL |
|:--------|:----|
| Search Application | `http://<minikube-ip>:30005` |
| Kibana Dashboard | `http://<minikube-ip>:30601` |
| Jenkins | `http://<minikube-ip>:30000` |
| Vault | `http://<minikube-ip>:<vault-nodeport>` |

## Appendix B: Commands Reference

```bash
# Start Minikube
minikube start

# Apply all K8s manifests
kubectl apply -f k8s/

# Deploy via Ansible
cd semantic-search-engine-main/ansible
ansible-playbook deploy.yml

# Check HPA status
kubectl get hpa

# View pod logs
kubectl logs -f deployment/python-search-app

# Get service URLs
minikube service list
```

---

**End of Report**
