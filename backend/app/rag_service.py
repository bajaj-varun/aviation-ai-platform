import os
import boto3
from pymongo import MongoClient
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.schema import Document
from dotenv import load_dotenv
import json
from typing import List, Dict, Any

load_dotenv()

# TODO: logging and metrics collection

class RAGService:
    def __init__(self):
        self.setup_clients()
        self.setup_vector_store()
    
    def setup_clients(self):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client['aviation_db']
        self.collection = self.db['aviation_docs']
    
    def setup_vector_store(self):
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_runtime,
            model_id=os.getenv("TEXT_EMBEDDING_MODEL")
        )
        
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name="aviation_vector_index",
            text_key="text"
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
    
    def ask_claude(self, question: str, context: str = "") -> str:
        """Simple method to ask Claude a question with context"""
        try:
            # prompt
            if context:
                prompt = f"""You are an aviation expert. Use this context to answer the question. 
Context: {context}
Question: {question}
Answer:"""
            else:
                prompt = f"Question: {question}\n\nAnswer:"
            
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.1,
                "messages": messages
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=os.getenv("REASONING_MODEL"),
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def query(self, question: str, context_type: str = "general") -> Dict[str, Any]:
        """Main query method"""
        try:
            docs = self.retriever.invoke(question)
            answer = self.ask_claude(question, context_type)
            
            return {
                "answer": answer,
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    } for doc in docs
                ],
                "question": question
            }
            
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "source_documents": [],
                "question": question
            }
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        docs = [Document(page_content=doc["text"], metadata=doc["metadata"]) 
                for doc in documents]
        self.vector_store.add_documents(docs)
