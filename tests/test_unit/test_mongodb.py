# Contents of test_win10_mongodb.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from unit.mongodb import MongoDB
from unittest.mock import patch

# import pytest

logger = logging.getLogger(__name__)

import json
import pytest
from unittest.mock import patch, mock_open

MDB_ATTR = [{
    "Log Path": '/home/pi/uart.log',
    "Report Path": ".report.json"
}]

# 模拟的聚合结果数据
AGGREGATE_RESULTS = [{
    "avg_read_bw": 115.0,
    # "max_read_bw": 130,
    # "min_read_bw": 100,
    # "std_read_bw": 12.909944,
    "avg_read_iops": 215.0,
    # "max_read_iops": 230,
    # "min_read_iops": 200,
    # "std_read_iops": 12.909944,
    "avg_write_bw": 165.0,
    # "max_write_bw": 180,
    # "min_write_bw": 150,
    # "std_write_bw": 12.909944,
    "avg_write_iops": 265.0
    # "max_write_iops": 280,
    # "min_write_iops": 250,
    # "std_write_iops": 12.909944
}]

class TestMongoDB:
    @pytest.fixture(scope="module")
    def mongo_db(self):
        print('\n\033[32m=============== Setup MongoDB ==============\033[0m')
        # Mock MongoDB client
        mock_client = patch('unit.mongodb.MongoClient').start()
        mock_db = mock_client.return_value['test_db']
        mock_collection = mock_db['test_collection']

        # Create instance of MongoDB class
        mongo_db_instance = MongoDB('localhost', 27017, 'test_db',
                                    'test_collection')
        
        yield mongo_db_instance, mock_collection
        print('\n\033[32m============= Teardown MongoDB ============\033[0m')
        patch.stopall()

    @pytest.mark.parametrize("attr", MDB_ATTR)
    def test_write_log_and_report(self, mongo_db, attr):
        mongo_db_instance, mock_collection = mongo_db
        log_path = attr["Log Path"]
        report_path = attr["Report Path"]
        
        # Mock the log file and report file contents
        mock_log_data = "Sample log data"
        mock_report_data = {"key": "value"}

        with patch("builtins.open",
                   mock_open(read_data=mock_log_data)) as mock_log_file, \
             patch("json.load", return_value=mock_report_data):
            
            mongo_db_instance.write_log_and_report(log_path, report_path)
            
            # Verify the file open calls
            mock_log_file.assert_any_call(log_path, 'r')
            mock_log_file.assert_any_call(report_path, 'r')

            # Verify the document insertion into MongoDB
            expected_document = {
                'log': mock_log_data,
                'report': mock_report_data
            }
            mock_collection.insert_one.assert_called_once_with(expected_document)
    
    def test_read_result(self, mongo_db):
        mongo_db_instance, mock_collection = mongo_db
        # Mock documents returned by MongoDB
        mock_documents = [{"key1": "value1"}, {"key2": "value2"}]
        mock_collection.find.return_value = mock_documents
        
        result_path = 'result.json'
        
        with patch("builtins.open", mock_open()) as mock_file:
            mongo_db_instance.read_result(result_path)
            
            # Verify the file write call
            mock_file.assert_called_once_with(result_path, 'w')
            
            # Retrieve the actual write calls
            handle = mock_file()
            written_data = handle.write.call_args_list
            
            # Convert written data back to JSON for comparison
            written_json = json.loads("".join(call[0][0] for call in written_data))
            
            assert written_json == mock_documents

    def test_update_document(self, mongo_db):
        mongo_db_instance, mock_collection = mongo_db
        filter_query = {"key": "value"}
        update_values = {"key": "new_value"}
        
        mock_update_result = mock_collection.update_one.return_value
        mock_update_result.matched_count = 1
        mock_update_result.modified_count = 1
        
        mongo_db_instance.update_document(filter_query, update_values)
        
        # Verify the update call
        mock_collection.update_one.assert_called_once_with(filter_query, {'$set': update_values})

    def test_delete_document(self, mongo_db):
        mongo_db_instance, mock_collection = mongo_db
        filter_query = {"key": "value"}
        
        mock_delete_result = mock_collection.delete_one.return_value
        mock_delete_result.deleted_count = 1
        
        mongo_db_instance.delete_document(filter_query)
        
        # Verify the delete call
        mock_collection.delete_one.assert_called_once_with(filter_query)

    def test_find_document(self, mongo_db):
        mongo_db_instance, mock_collection = mongo_db
        filter_query = {"key": "value"}
        mock_document = {"key": "value"}
        
        mock_collection.find_one.return_value = mock_document
        
        result = mongo_db_instance.find_document(filter_query)
        
        # Verify the find call and result
        mock_collection.find_one.assert_called_once_with(filter_query)
        assert result == mock_document

    @pytest.mark.parametrize("mock_aggregate_result", [AGGREGATE_RESULTS])
    def test_aggregate_random_metrics(self, mongo_db, mock_aggregate_result):
        mongo_db_instance, mock_collection = mongo_db
        
        mock_collection.aggregate.return_value = mock_aggregate_result
        
        # Call the aggregate_metrics method
        result = mongo_db_instance.aggregate_random_metrics(0, 1)
        
        # Verify the aggregate call
        mock_collection.aggregate.assert_called_once()
        
        # Check if the result is as expected
        assert result == mock_aggregate_result[0]
        
        if result:
            logger.debug(f'metrics = {json.dumps(result, indent=4)}')

