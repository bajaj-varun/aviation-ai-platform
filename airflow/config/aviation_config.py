import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# TODO: dev/stage/prod Env handling

# Snowflake Configuration
SNOWFLAKE_CONN_ID = "snowflake_aviation_conn"
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

# MongoDB Configuration
MONGODB_CONN_ID = "mongodb_aviation_conn"
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

# AWS Configuration
AWS_CONN_ID = "aws_default"
AWS_BEDROCK_REGION = os.getenv("AWS_REGION")

# Data Sources
DATA_SOURCES = {
    "flights": {
        "table": "flights",
        "columns": ["flight_number", "airline_code", "departure_airport", "arrival_airport"]
    },
    "cargo_manifests": {
        "table": "cargo_manifests", 
        "columns": ["flight_number", "waybill_number", "cargo_description", "hazardous_material"]
    },
    "aviation_docs": {
        "paths": [
            "/data/aviation/manuals",
            "/data/aviation/regulations", 
            "/data/aviation/procedures"
        ]
    }
}

# Vector Store Configuration
VECTOR_STORE_CONFIG = {
    "embedding_model": os.getenv("TEXT_EMBEDDING_MODEL"),
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "index_name": "aviation_vector_index"
}