# RAG-Chatbot
This project integrates Amazon Kendra with a Large Language Model (LLM) using LangChain, enabling conversational AI capabilities.
Solution Architecture
Below is a diagram that shows the overall workflow. Raw data is stored in the S3 bucket and we use our custom documents for the chatbot. Amazon Kendra is used to index the data sources and serves as a knowledge database. We use the Llama2 model as the LLM for text generation. Llama2 is deployed as a SageMaker endpoint by SageMaker JumpStart.
There are three main steps in the workflow of RAG: 
1) Users input requests through the Chatbot web interface built by Streamlit.
2) LangChain is used as an agent framework to orchestrate the different components; Once a request comes in, LangChain sends a search query to Kendra to retrieve the context that is relevant to the user request.
3) LangChain then sends a prompt that includes the user request and the relevant context to the LLM. The results from the LLM are sent back to users via the Chatbot web interface.  
 



Solution Walkthrough
Walk through of the steps to set up the RAG solution. 
Prerequisites:
AWS REGION – US-WEST-2 (OREGON) used for all services. Make sure that every service mentioned here in this document is created in the same region.
Data Sources required:
1.	Training Dataset for finetuning the model, making sure to format the dataset according to the prompt template and guidelines provided by Meta for LLAMA-2-7B-CHAT model.
2.	Supplementary Data documents for the Retrieval by the AWS Kendra service. The chatbot refers to these documents for answering. 
Setting up the S3-Bucket:
1.	Dump the data sources mentioned above in a s3-bucket for accessing them through the sagemaker and kendra.
2.	Create a S3 bucket and upload the files into the S3 bucket. Here in this case, the s3 bucket is named, my-chatbot-data.

 

NOTE: The supplementary documents for retrieval can be also provided through the chatbot interface itself. Refer to “Setting up and launching the chatbot application” section of this document.
Deploy a LLM from Amazon SageMaker Jumpstart:

1.	Go to SageMaker Studio. 
2.	Go to SageMaker Jumpstart, click “Models, notebooks, solutions”, and search for “Llama-2-7b-chat” model. 

 

1.	Select an EC2 instance type from the SageMaker hosting instance dropdown list. Note that you might need to request service quota increase if the selected EC2 instance is not available in your AWS account. Then give an Endpoint name that you would use later and click deploy. It might take 15-20 minutes to deploy the endpoint.  
3.	Once the endpoint deployment is finished, you should see the endpoint status showing in service.

 

To Fine-tune and deploy the fine-tuned model:

1.	Go to SageMaker Studio. 
2.	Go to SageMaker Jumpstart, click “Models, notebooks, solutions”, and search for “Llama-2-7b-chat” model. 
    

3.	Go to the train model section and choose the s3 bucket location where your training data resides and click on “Train”. This is one way of training the model on Sagemaker studio. We can also train the model programmatically via the notebook that AWS provides.
 




After the training job is finished it should look something like this:
 

4.	Deploy the model:
After the model is fine-tuned, you can deploy it using the model page on SageMaker JumpStart. The option to deploy the fine-tuned model will appear when fine-tuning is finished, as shown in the following screenshot.
 
Note the endpoint name, after the deployment is finished.

Index the data sources using Amazon Kendra: 

1.	Log into AWS account and search for Kendra.
2.	On the Kendra console, click Create an Index.
3.	Give an Index name and create a new role (recommended), as shown
. 
4.	Keep everything else as default and create the index. It can take a few minutes to create the index. 

5.	Once the index is created. Click add data sources. 

6.	Choose Amazon S3 connector.
 


7.	Specify the data source name and choose the language of the source documents. 
 

8.	Choose to create a new role, give the role a new name and leave everything else as default. 
 
9.	Choose the S3 location where the PDF is located and choose the Run on demand schedule. Leave everything else as default. 
 

10.	Go to the next page, leave everything else as default, and click add data source at the end. 
11.	Click the Sync now button on the Data sources page. It can take minutes to hours to finish the sync depending on the size of the documents. As a reference, for the documents size that has around 400 pages, it takes about 15 minutes to finish. 
After completion note the INDEX-ID for your data source.
 

Setting up and Launching the Chatbot application:

1.	Setup your preferred IDE, here Microsoft VSCODE is being used and copy the chatbot solution folder provided into your pc. 
2.	Before launching the chatbot, setting up the environment variables is necessary. As mentioned earlier specify the noted values of ENDPOINT NAME, KENDRA INDEX-ID and AWS-REGION in the .env file as shown below.
 
3.	Select Terminal -> New Terminal to create a new Terminal.
4.	On the terminal, run the commands below, the commands install the prerequisites, including LangChain, boto3 and Streamlit, and changes directory to working directory. Note: Folder names may vary.
cd aws_Kendra_llama2-chatbot
pip install -r requirements.txt
5.	To launch the Chatbot, run the command below. 

streamlit run app.py llama2
When the application runs successfully, you will see an output similar to the one shown below. Find the port number in the output, where the port number is typically 8501.
You can now view your Streamlit app in your browser.
Network URL: http://169.255.255.2:8501
External URL: http://35.170.135.114:8501 

Uploading Data through the chat interface:

1.	The documents (supplementary documents meant for the retrieval) can be uploaded from the chat interface itself. 
2.	Click on the Browse Files button to upload files from your pc.
 
A window should pop up prompting you to upload files. After uploading the data directly gets uploaded to the s3 location which will be specified in the code.
 
Below shows two testing questions and answers returned by the RAG solution. By clicking the Sources button, it shows the data sources, such as the S3 location of the PDF files. 
Note: 
1.The chatbot responses also depend on the quality of the data you provide through Kendra and also the training data during the finetuning process.
2.The chatbot also responds to general questions and it also responds from the documents when necessary.
  


 

 
2. Launch the Chatbot application on EC2 instances
You can also run the Chatbot application on an EC2 instance. For doing this, all the steps remain the same, you can directly click the output URL that contains the port number. This link shows how to set up an EC2 instance. Make sure that the region of the EC2 instance is the same as where the SageMaker endpoint and Kendra are launched.  

