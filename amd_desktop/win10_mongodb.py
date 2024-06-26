'''Copyright (c) 2024 Jaron Cheng'''
# from pymongo import MongoClient

# # 使用本地 IP 地址連接 MongoDB
# client = MongoClient('mongodb://192.168.0.128:27017')

# # 選擇數據庫和集合
# db = client['test_database']
# collection = db['test_collection']

# # 插入文檔
# document = {
#     'name': 'Alice',
#     'age': 30,
#     'city': 'New York'
# }
# collection.insert_one(document)

# print("Data inserted successfully")
import json
from pymongo import MongoClient

class Win10MongoDB(object):
    def __init__(self,
                host='192.168.0.128',
                port=27017,
                db_name='AutoRAID',
                collection_name='amd_desktop'):
        self.client = MongoClient(f'mongodb://{host}:{port}')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def write_log_and_report(self,
                             log_path='~/Projects/AutoRAID/uart.log',
                             report_path='.report.json'):
        # 讀取uart.log文件
        with open(log_path, 'r') as log_file:
            log_data = log_file.read()
        
        # 讀取.report.json文件
        with open(report_path, 'r') as report_file:
            report_data = json.load(report_file)
        
        # 創建插入文檔
        document = {
            'log': log_data,
            'report': report_data
        }
        
        # 插入文檔到集合
        self.collection.insert_one(document)
        print("Log and report inserted successfully")

    def read_result(self, result_path='result.json'):
        # 從集合中讀取數據
        documents = self.collection.find()
        
        # 將數據寫入result.json文件
        with open(result_path, 'w') as result_file:
            json.dump(list(documents), result_file, default=str)
        
        print("Result written to result.json")

# 示例用法
# if __name__ == "__main__":
#     mongo_db = Win10MongoDB()
#     mongo_db.write_log_and_report('uart.log', '.report.json')
#     mongo_db.read_result('result.json')
