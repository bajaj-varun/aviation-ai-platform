import unittest
import sys
import os

from unittest.mock import MagicMock
from datetime import datetime

from airflow.models.dag import DAG
from airflow.models import TaskInstance

# Include custom operator path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'plugins')))

from aviation_operators import (
    DocumentChunkingOperator,
    VectorEmbeddingOperator,
    MongoDBIndexOperator
)

DEFAULT_DATE = datetime(2025, 1, 1)

class TestDocumentChunkingOperator(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.dag = DAG(dag_id='test_dag', start_date=DEFAULT_DATE)

    def test_my_custom_operator_execute(self):
        operator = DocumentChunkingOperator(task_id='my_task', my_param='test_value', dag=self.dag)

        # Create a TaskInstance to simulate execution context
        ti = TaskInstance(task=operator, execution_date=DEFAULT_DATE)

        # Call the execute method and assert the expected behavior
        result = operator.execute(context=ti.get_template_context())
        self.assertEqual(result, 'expected_output')


if __name__=="main":
    unittest.main()