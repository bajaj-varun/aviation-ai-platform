import os
import boto3
from pymongo import MongoClient
from langchain_aws.embeddings import BedrockEmbeddings
# from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_aws import BedrockLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv
import json

load_dotenv()

class RAGService:
    def __init__(self):
        self.setup_clients()
        self.setup_vector_store()
        self.setup_llm()
    
    def setup_clients(self):
        # AWS Bedrock client
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION')
        )
        
        # MongoDB client
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client['aviation_db']
        self.collection = self.db['aviation_docs']
    
    def setup_vector_store(self):
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_runtime,
            
            # model_id=os.getenv('TEXT_EMBEDDING_MODEL')
            model_id="amazon.titan-embed-text-v2:0"
        )
        
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name="aviation_vector_index",
            text_key="text"
        )
    
    def setup_llm(self):
        self.llm = BedrockLLM(
            client=self.bedrock_runtime,
            # model_id=os.getenv('REASONING_MODEL'),
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
            model_kwargs={
                "max_tokens_to_sample": 1000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        # Custom prompt template for aviation domain
        self.prompt_template = PromptTemplate(
            template="""You are an expert aviation operations assistant. Use the following context to answer the question accurately and concisely.

Context: {context}

Question: {question}

If the context doesn't contain relevant information, say so and does not hallucinate.

Answer:""",
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def query(self, question: str, context_type: str = "general"):
        # Add context type filtering if needed
        if context_type != "general":
            question = f"{context_type.upper()} CONTEXT: {question}"
        
        result = self.qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in result["source_documents"]
            ],
            "question": question
        }
    
    def add_documents(self, documents: list):
        """Add documents to the vector store"""
        docs = [Document(page_content=doc["text"], metadata=doc["metadata"]) 
                for doc in documents]
        self.vector_store.add_documents(docs)
