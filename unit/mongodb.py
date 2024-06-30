'''Copyright (c) 2024 Jaron Cheng'''
import json
from pymongo import MongoClient, errors

# class MongoDB(object):
#     def __init__(self, host, port, db_name, collection_name):
#                 # host='192.168.0.128',
#                 # port=27017,
#                 # db_name='AutoRAID',
#                 # collection_name='amd_desktop'):
#         self.client = MongoClient(f'mongodb://{host}:{port}')
#         self.db = self.client[db_name]
#         self.collection = self.db[collection_name]

#     def write_log_and_report(self, log_path, report_path):
#                             #  log_path='~/Projects/AutoRAID/uart.log',
#                             #  report_path='.report.json'):
#         # 讀取uart.log文件
#         with open(log_path, 'r') as log_file:
#             log_data = log_file.read()
        
#         # 讀取.report.json文件
#         with open(report_path, 'r') as report_file:
#             report_data = json.load(report_file)
        
#         # 創建插入文檔
#         document = {
#             'log': log_data,
#             'report': report_data
#         }
        
#         # 插入文檔到集合
#         self.collection.insert_one(document)
#         print("Log and report inserted successfully")

#     def read_result(self, result_path='result.json'):
#         # 從集合中讀取數據
#         documents = self.collection.find()
        
#         # 將數據寫入result.json文件
#         with open(result_path, 'w') as result_file:
#             json.dump(list(documents), result_file, default=str)
        
#         print("Result written to result.json")


class MongoDB(object):
    def __init__(self, host, port, db_name, collection_name):
        self.client = MongoClient(f'mongodb://{host}:{port}')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def write_log_and_report(self, log_path, report_path):
        try:
            with open(log_path, 'r') as log_file:
                log_data = log_file.read()
        except FileNotFoundError:
            print(f"Error: The file {log_path} was not found.")
            return
        except IOError as e:
            print(f"Error reading {log_path}: {e}")
            return

        try:
            with open(report_path, 'r') as report_file:
                report_data = json.load(report_file)
        except FileNotFoundError:
            print(f"Error: The file {report_path} was not found.")
            return
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {report_path}: {e}")
            return

        document = {
            'log': log_data,
            'report': report_data
        }

        try:
            self.collection.insert_one(document)
            print("Log and report inserted successfully")
        except errors.PyMongoError as e:
            print(f"Error inserting document into MongoDB: {e}")

    def read_result(self, result_path='result.json'):
        try:
            documents = self.collection.find()
            documents_list = list(documents)
        except errors.PyMongoError as e:
            print(f"Error reading from MongoDB: {e}")
            return

        try:
            with open(result_path, 'w') as result_file:
                json.dump(documents_list, result_file, default=str)
            print("Result written to result.json")
        except IOError as e:
            print(f"Error writing to {result_path}: {e}")

    def update_document(self, filter_query, update_values):
        try:
            result = self.collection.update_one(filter_query, {'$set': update_values})
            if result.matched_count:
                print(f"Document updated successfully: {result.modified_count} document(s) modified.")
            else:
                print("No document matches the given query.")
        except errors.PyMongoError as e:
            print(f"Error updating document: {e}")

    def delete_document(self, filter_query):
        try:
            result = self.collection.delete_one(filter_query)
            if result.deleted_count:
                print(f"Document deleted successfully: {result.deleted_count} document(s) deleted.")
            else:
                print("No document matches the given query.")
        except errors.PyMongoError as e:
            print(f"Error deleting document: {e}")

    def find_document(self, filter_query):
        try:
            document = self.collection.find_one(filter_query)
            if document:
                return document
            else:
                print("No document matches the given query.")
                return None
        except errors.PyMongoError as e:
            print(f"Error finding document: {e}")
            return None

