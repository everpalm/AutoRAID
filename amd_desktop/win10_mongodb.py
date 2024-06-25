'''Copyright (c) 2024 Jaron Cheng'''
from pymongo import MongoClient

# 使用本地 IP 地址連接 MongoDB
client = MongoClient('mongodb://192.168.0.128:27017')

# 選擇數據庫和集合
db = client['test_database']
collection = db['test_collection']

# 插入文檔
document = {
    'name': 'Alice',
    'age': 30,
    'city': 'New York'
}
collection.insert_one(document)

print("Data inserted successfully")
