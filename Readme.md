# Amazon Kendra LangChain Extensions

## Overview

This repository contains Python scripts for integrating Amazon Kendra with SageMaker's Large Language Models (LLMs) using the LangChain framework. It includes:

- `kendra_chat_llama_2.py`: A script for conversational retrieval using Amazon Kendra and a SageMaker LLM endpoint.
- `app.py`: A Streamlit-based web application to interact with the Kendra-LLM integration in a user-friendly manner.

## Prerequisites

- Python 3.x
- Access to Amazon Kendra and AWS SageMaker services.
- Basic understanding of AWS services and Python programming.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone [repository-url]
   cd aws-kendra-llama2-chatbot
   ```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

## Configuration
**Set Up AWS Credentials:**

Ensure your AWS credentials are configured correctly, typically via the AWS CLI.

**Environment Variables:**

Set the necessary environment variables via environment variables at a system level or via .env file

export AWS_REGION = "us-east-1"

export KENDRA_INDEX_ID = "index-id"

export LLAMA_2_ENDPOINT = "sagemaker-endpoint-id"

## Usage
### Running the Kendra Chat Script

- kendra_chat_llama_2.py integrates Amazon Kendra with a SageMaker LLM for conversational query processing.
- Before running the script, ensure the deployment of your LLM on SageMaker and note the endpoint name.
- Execute the script in a Python environment.

### Using the Streamlit Web Application
```bash
streamlit run app.py llama2
```
   
## Features
- Kendra Integration: Leverages Amazon Kendra for advanced search and query capabilities.
- SageMaker LLM Endpoint: Utilizes a deployed LLM on SageMaker for natural language processing.
- Conversational Interface: Offers a conversational approach to query Amazon Kendra through the LLM.
- Streamlit Web App: Provides a graphical interface for a more intuitive user experience.
