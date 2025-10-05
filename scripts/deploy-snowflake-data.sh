#!/bin/bash

# the script should be run as 
# chmod +x scripts/deploy-snowflake-data.sh
# ./scripts/deploy-snowflake-data.sh

echo "Starting Snowflake Data Deployment..."

# Load environment variables
source .env

# Execute SQL files
echo "Creating database structure..."
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USER -d AVIATION_DB -s AVIATION_DATA -f scripts/snowflake-setup.sql

echo "Loading sample data..."
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USER -d AVIATION_DB -s AVIATION_DATA -f scripts/sample-data-insertion.sql

# Run Python data loader
echo "Running Python data loader..."
python scripts/load_sample_data.py

echo "Data validation..."
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USER -d AVIATION_DB -s AVIATION_DATA -f scripts/validation-queries.sql

echo "Snowflake data deployment completed!"