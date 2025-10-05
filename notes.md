# Architecture Diagram: GenAI-Powered Aviation Operational Intelligence Platform

The architecture is built on AWS and consists of four main layers: Data Ingestion & Orchestration, Data Storage & Processing, AI & Application Layer, and Security & Operations, all unified by CI/CD & GitOps.

## Layer 1: Data Ingestion & Orchestration

This layer is responsible for collecting all data from various sources and managing the pipelines.

1. Data Sources:
    - SITA/ARINC: Real-time flight status data streams.

    - Cargo Systems: CargoXML messages for waybills and manifests.

    - Maintenance Systems: IoT sensor data from aircraft and cargo pallets, maintenance logs.

    - Document Repositories: IATA regulations, Aircraft Maintenance Manuals (PDFs, Docs).

2. Orchestration & Ingestion:

    - Apache Airflow: Sits at the center of this layer.

    - Airflow DAGs trigger and monitor data pipelines.

    - Custom Airflow operators (Python) pull data from APIs, message queues, and cloud storage.

    - One dedicated DAG handles the document processing for the RAG pipeline, chunking documents and sending them to the embedding model.

## Layer 2: Data Storage & Processing

This layer stores and transforms the data for both analytics and AI.

1. Vector Store:

    - MongoDB Atlas: Acts as the Vector Database.

    - Flow: Processed text chunks from Airflow are converted into vectors via an AWS Bedrock (Titan Embeddings) model and stored in MongoDB.

    - Stores the embedded document chunks and their metadata.

2. Data Warehouse:

    - Snowflake: The central structured data warehouse.

    - Flow: Raw data from Airflow is loaded into Snowflake.

    - DBT (Data Build Tool) runs inside Snowflake to transform raw data into clean, modeled tables (e.g., fact_flights, dim_aircraft).

## Layer 3: AI & Application Layer

This is the core intelligence and user-facing part of the platform, running on Kubernetes.

1. Runtime Environment:

    - Amazon EKS (Kubernetes): Hosts all microservices.

    - Managed and visualized using Rancher.

2. AI Microservices (Deployed on EKS):

    - RAG Service (Python):

        - Uses LangChain to orchestrate the RAG workflow.

        - Receives a user query -> retrieves relevant chunks from MongoDB (Vector DB) -> formulates a prompt -> calls AWS Bedrock (Claude/Titan) -> returns a grounded, contextual response.

    - Data API Service (NodeJS):

        - Provides RESTful APIs for the frontend to query structured data from Snowflake (e.g., flight lists, cargo status).

3. Frontend:

    - A React.js web application (not in the core stack but implied) that interacts with the AI and Data APIs, providing the UI for operational staff.

## Layer 4: Security, Governance & Monitoring

This cross-cutting layer ensures security, observability, and audit.

1. Security:

    - AWS IAM: Manages fine-grained permissions for all AWS services (Bedrock, EKS, S3).

    - AWS Secrets Manager: Stores and rotates database credentials, API keys, and other secrets. The EKS pods retrieve secrets from here.

2. Governance:

    - AWS CloudTrail: Logs all API activity across the AWS account for audit and compliance.

3. Monitoring:

    - Prometheus & Grafana: Scrape and visualize metrics from EKS, NodeJS, and Python services.

    - EFK Stack (Elasticsearch, Fluentd, Kibana): Aggregates and analyzes application logs from all pods for debugging and support.

## Unifying Layer: CI/CD & GitOps

This automated pipeline underpins the entire development and deployment process.

1. Source Code:
    - Code for all microservices, DBT models, Airflow DAGs, and Kubernetes manifests is stored in a Git repository (e.g., GitHub).

2. CI/CD Pipeline:
    - Jenkins / GitHub Actions: Triggered on a git push.

        - Steps:

            - Build Docker images for the NodeJS and Python services.

            - Test code (unit tests with Jest/pyTest) and scan for vulnerabilities and quality (SonarQube).

            - Push the validated images to a Docker Registry (e.g., ECR).

3. GitOps Deployment:

    - ArgoCD: Continuously monitors the git repository for changes to the Kubernetes manifests.

        - Automatically deploys the new application images and configuration to the EKS cluster, ensuring the state of the cluster matches the state defined in git.

## Data Flow Summary

- Data Ingest: External data sources are ingested via Airflow DAGs.

- Data Process & Store: Structured data is cleaned with DBT in Snowflake. Unstructured documents are embedded and stored in MongoDB Vector DB.

- User Query: A user asks a question in the frontend.

- RAG Process: The query goes to the RAG Service on EKS, which retrieves context from MongoDB and generates a smart response using AWS Bedrock.

- Support & Ops: The entire platform is secured by IAM & Secrets Manager, monitored by Prometheus/Grafana, and all changes are audited by CloudTrail.
