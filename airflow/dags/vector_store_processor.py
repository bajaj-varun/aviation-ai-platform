from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# import sys, os
# sys.path.append('../config')
# sys.path.append('../plugins')

from aviation_operators import (
    DocumentChunkingOperator,
    VectorEmbeddingOperator,
    MongoDBIndexOperator
)

from aviation_config import *

default_args = {
    'owner': 'aviation_ai',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=10)
}

with DAG(
    'vector_store_processor',
    default_args=default_args,
    description='Process aviation documents and create vector embeddings',
    # schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['aviation', 'vector_store', 'mongodb', 'embeddings']
) as dag:

    start_processing = EmptyOperator(task_id='start_processing')

    # Chunk documents for processing
    chunk_documents = DocumentChunkingOperator(
        task_id='chunk_documents',
        message='DocumentChunkingOperator test',
        source_paths=DATA_SOURCES['aviation_docs']['paths'],
        chunk_size=VECTOR_STORE_CONFIG['chunk_size'],
        chunk_overlap=VECTOR_STORE_CONFIG['chunk_overlap'],
        output_path='/tmp/aviation_chunks/'
    )

    # Generate embeddings using AWS Bedrock
    generate_embeddings = VectorEmbeddingOperator(
        task_id='generate_embeddings',
        input_path='/tmp/aviation_chunks/',
        aws_conn_id=AWS_CONN_ID,
        model_id=VECTOR_STORE_CONFIG['embedding_model'],
        output_path='/tmp/aviation_embeddings/'
    )

    # Store embeddings in MongoDB
    store_embeddings = MongoDBIndexOperator(
        task_id='store_embeddings',
        message="store_embeddings",
        embeddings_path='/tmp/aviation_embeddings/',
        mongodb_conn_id=MONGODB_CONN_ID,
        database_name=MONGODB_DATABASE,
        collection_name=MONGODB_COLLECTION,
        index_name=VECTOR_STORE_CONFIG['index_name']
    )

    # Create vector search index
    create_vector_index = PythonOperator(
        task_id='create_vector_index',
        python_callable=create_mongodb_vector_index,
        op_kwargs={
            'mongodb_conn_id': MONGODB_CONN_ID,
            'database_name': MONGODB_DATABASE,
            'collection_name': MONGODB_COLLECTION,
            'index_name': VECTOR_STORE_CONFIG['index_name']
        }
    )

    # Validate vector store
    validate_vector_store = PythonOperator(
        task_id='validate_vector_store',
        python_callable=validate_vector_embeddings,
        op_kwargs={
            'mongodb_conn_id': MONGODB_CONN_ID,
            'collection_name': MONGODB_COLLECTION
        }
    )

    end_processing = DummyOperator(task_id='end_processing')

    # Define workflow
    start_processing >> chunk_documents >> generate_embeddings >> store_embeddings
    store_embeddings >> create_vector_index >> validate_vector_store >> end_processing

def create_mongodb_vector_index(mongodb_conn_id, database_name, collection_name, index_name):
    """Create vector search index in MongoDB"""
    from airflow.providers.mongo.hooks.mongo import MongoHook
    import pymongo
    
    hook = MongoHook(mongodb_conn_id)
    client = hook.get_conn()
    db = client[database_name]
    collection = db[collection_name]
    
    # Create vector search index
    index_definition = {
        'fields': [
            {
                'type': 'vector',
                'path': 'embedding',
                'numDimensions': 1536,  # Titan embedding dimensions
                'similarity': 'cosine'
            },
            {
                'type': 'filter',
                'path': 'metadata.category'
            }
        ]
    }
    
    # Create search index
    db.command({
        'createSearchIndexes': collection_name,
        'indexes': [{
            'name': index_name,
            'definition': index_definition
        }]
    })
    
    print(f"Vector index '{index_name}' created successfully")

def validate_vector_embeddings(mongodb_conn_id, collection_name):
    """Validate that embeddings were created correctly"""
    from airflow.providers.mongo.hooks.mongo import MongoHook
    
    hook = MongoHook(mongodb_conn_id)
    client = hook.get_conn()
    db = client[MONGODB_DATABASE]
    collection = db[collection_name]
    
    # Count documents with embeddings
    total_docs = collection.count_documents({})
    docs_with_embeddings = collection.count_documents({'embedding': {'$exists': True}})
    
    print(f"Total documents: {total_docs}")
    print(f"Documents with embeddings: {docs_with_embeddings}")
    
    if docs_with_embeddings == 0:
        raise ValueError("No documents with embeddings found!")
    
    if docs_with_embeddings < total_docs * 0.9:  # At least 90% should have embeddings
        raise ValueError(f"Only {docs_with_embeddings}/{total_docs} documents have embeddings")