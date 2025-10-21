from airflow.models.baseoperator import BaseOperator
# from airflow.utils.decorators import apply_defaults
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
import boto3
import json
import os
from typing import List, Dict
import PyPDF2
from docx import Document
# import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

class ProcessAviationDocumentsOperator(BaseOperator):
    """
    Operator to process aviation documents and prepare for vector storage
    """
    
    # @apply_defaults
    def __init__(
        self,
        document_paths: List[str],
        mongodb_conn_id: str,
        aws_conn_id: str,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.document_paths = document_paths
        self.mongodb_conn_id = mongodb_conn_id
        self.aws_conn_id = aws_conn_id

    def execute(self, context):
        self.log.info("Starting aviation document processing")
        
        # Process documents from all paths
        processed_docs = []
        for path in self.document_paths:
            if os.path.exists(path):
                docs = self._process_documents_in_path(path)
                processed_docs.extend(docs)
        
        # Store in MongoDB
        self._store_documents(processed_docs)
        
        self.log.info(f"Processed {len(processed_docs)} documents")
        return len(processed_docs)

    def _process_documents_in_path(self, path: str) -> List[Dict]:
        """Process all documents in a given path"""
        documents = []
        
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if filename.endswith('.pdf'):
                content = self._read_pdf(file_path)
            elif filename.endswith('.docx'):
                content = self._read_docx(file_path)
            elif filename.endswith('.txt'):
                content = self._read_txt(file_path)
            else:
                continue
            
            if content:
                documents.append({
                    'filename': filename,
                    'content': content,
                    'file_path': file_path,
                    'processed_at': context['ts'],
                    'metadata': {
                        'source': 'aviation_docs',
                        'category': self._categorize_document(filename),
                        'file_type': filename.split('.')[-1]
                    }
                })
        
        return documents

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            self.log.error(f"Error reading PDF {file_path}: {e}")
            return ""

    def _read_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            self.log.error(f"Error reading DOCX {file_path}: {e}")
            return ""

    def _read_txt(self, file_path: str) -> str:
        """Read text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.log.error(f"Error reading TXT {file_path}: {e}")
            return ""

    def _categorize_document(self, filename: str) -> str:
        """Categorize document based on filename"""
        filename_lower = filename.lower()
        if 'regulation' in filename_lower or 'iata' in filename_lower:
            return 'regulations'
        elif 'maintenance' in filename_lower or 'procedure' in filename_lower:
            return 'maintenance'
        elif 'cargo' in filename_lower or 'loading' in filename_lower:
            return 'cargo'
        elif 'safety' in filename_lower:
            return 'safety'
        else:
            return 'general'

    def _store_documents(self, documents: List[Dict]):
        """Store processed documents in MongoDB"""
        hook = MongoHook(self.mongodb_conn_id)
        client = hook.get_conn()
        db = client[MONGODB_DATABASE]
        collection = db['processed_documents']
        
        if documents:
            collection.insert_many(documents)
            self.log.info(f"Stored {len(documents)} documents in MongoDB")

class VectorEmbeddingOperator(BaseOperator):
    """
    Operator to generate vector embeddings using AWS Bedrock
    """
    
    # @apply_defaults
    def __init__(
        self,
        input_path: str,
        aws_conn_id: str,
        model_id: str,
        output_path: str,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_path = input_path
        self.aws_conn_id = aws_conn_id
        self.model_id = model_id
        self.output_path = output_path

    def execute(self, context):
        self.log.info("Starting vector embedding generation")
        
        # Initialize AWS Bedrock client
        aws_hook = AwsBaseHook(self.aws_conn_id, client_type='bedrock-runtime')
        bedrock_client = aws_hook.get_conn()
        
        # Process documents and generate embeddings
        embeddings = []
        for filename in os.listdir(self.input_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.input_path, filename)
                with open(file_path, 'r') as f:
                    doc_data = json.load(f)
                
                embedding = self._generate_embedding(bedrock_client, doc_data['content'])
                if embedding:
                    doc_data['embedding'] = embedding
                    embeddings.append(doc_data)
        
        # Save embeddings
        os.makedirs(self.output_path, exist_ok=True)
        for i, emb_data in enumerate(embeddings):
            output_file = os.path.join(self.output_path, f"embedding_{i}.json")
            with open(output_file, 'w') as f:
                json.dump(emb_data, f, indent=2)
        
        self.log.info(f"Generated {len(embeddings)} embeddings")
        return len(embeddings)

    def _generate_embedding(self, bedrock_client, text: str) -> List[float]:
        """Generate embedding using AWS Bedrock"""
        try:
            if not text or len(text.strip()) == 0:
                return None
                
            response = bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({'inputText': text[:10000]})  # Limit text length
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding')
            
        except Exception as e:
            self.log.error(f"Error generating embedding: {e}")
            return None

class DataQualityCheckOperator(BaseOperator):
    """
    Operator to perform data quality checks on Snowflake tables
    """
    
    # @apply_defaults
    def __init__(
        self,
        table_name: str,
        checks: List[Dict],
        snowflake_conn_id: str = 'snowflake_default',
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.checks = checks
        self.snowflake_conn_id = snowflake_conn_id

    def execute(self, context):
        self.log.info(f"Running data quality checks for {self.table_name}")
        
        from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
        hook = SnowflakeHook(snowflake_conn_id=self.snowflake_conn_id)
        
        failed_checks = []
        
        for check in self.checks:
            check_sql = check['check_sql']
            expected_result = check['expected_result']
            
            result = hook.get_first(check_sql)[0]
            
            if result != expected_result:
                failed_checks.append({
                    'check_sql': check_sql,
                    'expected': expected_result,
                    'actual': result
                })
                self.log.error(f"Data quality check failed: {check_sql}")
        
        if failed_checks:
            error_msg = f"Data quality checks failed for {self.table_name}: {failed_checks}"
            raise ValueError(error_msg)
        
        self.log.info(f"All data quality checks passed for {self.table_name}")
        return f"All checks passed for {self.table_name}"

# Additional operators for document processing
class DocumentChunkingOperator(BaseOperator):
    """Operator to chunk documents for vector processing"""
    # @apply_defaults
    def __init__(self, message, 
                 source_paths:list[str], 
                 chunk_size:int, 
                 chunk_overlap:int,  
                 output_path:str, 
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.source_paths   = source_paths
        self.chunk_size     = chunk_size
        self.chunk_overlap  = chunk_overlap
        self.output_path    = output_path

    # TODO: business logic

    def execute(self, context):
        self.log.info("Chunking documents for vector processing")
        # Implementation for document chunking
        return "Documents chunked successfully"

class MongoDBIndexOperator(BaseOperator):
    """Operator to store embeddings in MongoDB"""
    # @apply_defaults
    def __init__(self, 
                 message:str,
                 embeddings_path:str,
                 mongodb_conn_id:str,
                 database_name:str,
                 collection_name:str,
                 index_name:str,
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.message        = message
        self.embeddings_path = embeddings_path
        self.mongodb_conn_id = mongodb_conn_id
        self.database_name = database_name
        self.collection_name = collection_name
        self.index_name = index_name

    def execute(self, context):
        self.log.info("Storing embeddings in MongoDB")
        # Implementation for MongoDB storage
        return "Embeddings stored in MongoDB"
    
class UpdateVectorStoreOperator(BaseOperator):
    """UpdateVectorStoreOperator embeddings in MongoDB"""
    # TODO: business logic
    # @apply_defaults
    def __init__(self, 
                 message:str,
                 mongodb_conn_id:str,
                 aws_conn_id:str,
                 collection_name:str,
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.mongodb_conn_id = mongodb_conn_id
        self.aws_conn_id = aws_conn_id
        self.collection_name = collection_name

    def execute(self, context):
        self.log.info("UpdateVectorStoreOperator")
        # Implementation for MongoDB storage
        return "UpdateVectorStoreOperator"