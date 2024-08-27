'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
from pymongo import MongoClient, errors
from pymongo import DESCENDING

logger = logging.getLogger(__name__)


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
            logger.error(f"Error: The file {log_path} was not found.")
            return
        except IOError as e:
            logger.critical(f"Error reading {log_path}: {e}")
            return

        try:
            with open(report_path, 'r') as report_file:
                report_data = json.load(report_file)
        except FileNotFoundError:
            logger.error(f"Error: The file {report_path} was not found.")
            return
        except json.JSONDecodeError as e:
            logger.critical(f"Error decoding JSON from {report_path}: {e}")
            return

        document = {
            'log': log_data,
            'report': report_data
        }

        try:
            self.collection.insert_one(document)
            logger.debug("Log and report inserted successfully")
        except errors.PyMongoError as e:
            logger.debug(f"Error inserting document into MongoDB: {e}")

    def read_result(self, result_path='result.json'):
        try:
            documents = self.collection.find()
            documents_list = list(documents)
        except errors.PyMongoError as e:
            logger.error(f"Error reading from MongoDB: {e}")
            return

        try:
            with open(result_path, 'w') as result_file:
                json.dump(documents_list, result_file, default=str)
            logger.debug("Result written to result.json")
        except IOError as e:
            logger.critical(f"Error writing to {result_path}: {e}")

    def update_document(self, filter_query, update_values):
        try:
            result = self.collection.update_one(filter_query, {'$set': update_values})
            if result.matched_count:
                logger.debug(f"Document updated successfully: {result.modified_count} document(s) modified.")
            else:
                logger.debug("No document matches the given query.")
        except errors.PyMongoError as e:
            logger.critical(f"Error updating document: {e}")

    def delete_document(self, filter_query):
        try:
            result = self.collection.delete_one(filter_query)
            if result.deleted_count:
                logger.debug(f"Document deleted successfully: {result.deleted_count} document(s) deleted.")
            else:
                logger.debug("No document matches the given query.")
        except errors.PyMongoError as e:
            logger.error(f"Error deleting document: {e}")

    def find_document(self, filter_query):
        try:
            document = self.collection.find_one(filter_query)
            if document:
                return document
            else:
                logger.debug("No document matches the given query.")
                return None
        except errors.PyMongoError as e:
            logger.critical(f"Error finding document: {e}")
            return None
        
    def aggregate_random_metrics(self, write_pattern, io_depth):
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "report.tests.keywords": 1,
                    "report.tests.call.log.msg": 1
                }
            },
            { "$unwind": { "path": "$report.tests" } },
            { "$unwind": { "path": "$report.tests.keywords" } },
            {
                "$match": {
                    "report.tests.keywords": {
                        "$regex": "test_run_io_operation"
                    }
                }
            },
            { "$unwind": { "path": "$report.tests.call" } },
            { "$unwind": { "path": "$report.tests.call.log" } },
            {
                "$project": {
                    "msg": "$report.tests.call.log.msg",
                    "write_pattern_string": {
                        "$regexFind": {
                            "input": "$report.tests.keywords",
                            "regex": "test_run_io_operation\\[(\\d+)-(\\d+)\\]"
                        }
                    }
                }
            },
            {
                "$project": {
                    "msg": 1,
                    "write_pattern": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_pattern_string.captures",
                                    0
                                ]
                            },
                            "to": "int",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "io_depth": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_pattern_string.captures",
                                    1
                                ]
                            },
                            "to": "int",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            {
                "$project": {
                    "write_pattern": 1,
                    "io_depth": 1,
                    "read_iops_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "random_read_iops = (\\d+.\\d+)"
                        }
                    },
                    "read_bw_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "random_read_bw = (\\d+.\\d+)"
                        }
                    },
                    "write_iops_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "random_write_iops = (\\d+.\\d+)"
                        }
                    },
                    "write_bw_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "random_write_bw = (\\d+.\\d+)"
                        }
                    }
                }
            },
            {
                "$project": {
                    "write_pattern": 1,
                    "io_depth": 1,
                    "read_iops": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$read_iops_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "read_bw": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$read_bw_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "write_iops": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_iops_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "write_bw": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_bw_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            { "$match": { "write_pattern": write_pattern ,
                         "io_depth": io_depth
                        } 
            },
            {
                "$group": {
                    "_id": {
                        "write_pattern": "$write_pattern",
                        "io_depth": "$io_depth"
                    },
                    "avg_read_iops": { "$avg": "$read_iops" },
                    "avg_read_bw": { "$avg": "$read_bw" },
                    "std_dev_read_iops": {"$stdDevPop": "$read_iops"},
                    "avg_write_iops": { "$avg": "$write_iops" },
                    "avg_write_bw": { "$avg": "$write_bw" },
                    "std_dev_write_iops": {"$stdDevPop": "$write_iops"}
                }
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.error(f"Error performing aggregation: {e}")
            return None

    def aggregate_sequential_metrics(self, write_pattern, io_depth):
        pipeline = [
                        # Stage 1
                        {
                            "$project": {
                                "_id": 0,
                                "report.tests.keywords": 1,
                                "report.tests.call.log.msg": 1
                            }
                        },
                        # Stage 2
                        { "$unwind": { "path": "$report.tests" } },
                        # Stage 3
                        { "$unwind": { "path": "$report.tests.keywords" } },
                        # Stage 4
                        {
                            "$project": {
                                "write_pattern_string": {
                                    "$regexFind": {
                                        "input": "$report.tests.keywords",
                                        "regex": "test_run_io_operation\\[(\\d+)-([\\dk]+)\\]"
                                    }
                                },
                                "msg": "$report.tests.call.log.msg"
                            }
                        },
                        # Stage 5
                        {
                            "$match": {
                                "$or": [
                                    {
                                        "write_pattern_string.match": {
                                            "$regex": "test_run_io_operation"
                                        }
                                    },
                                    {
                                        "report.tests.call.log.msg": {
                                            "$regex": "write_pattern"
                                        }
                                    }
                                ]
                            }
                        },
                        # Stage 6
                        {
                            "$project": {
                                "write_pattern": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$write_pattern_string.captures",
                                                0
                                            ]
                                        },
                                        "to": "double",
                                        "onError": None,
                                        "onNull": None
                                    }
                                },
                                "block_size": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$write_pattern_string.captures",
                                                1
                                            ]
                                        },
                                        "to": "string",
                                        "onError": None,
                                        "onNull": None
                                    }
                                },
                                "msg": 1
                            }
                        },
                        # Stage 7
                        { "$unwind": { "path": "$msg" } },
                        # Stage 8
                        { "$match": { "msg": { "$regex": "sequential" } } },
                        # Stage 9
                        {
                            "$project": {
                                "write_pattern": 1,
                                "block_size": 1,
                                "read_iops_string": {
                                    "$regexFind": {
                                        "input": "$msg",
                                        "regex": "sequential_read_iops\\s*=\\s*([\\d\\.]+)"
                                    }
                                },
                                "read_bw_string": {
                                    "$regexFind": {
                                        "input": "$msg",
                                        "regex": "sequential_read_bw\\s*=\\s*([\\d\\.]+)"
                                    }
                                },
                                "write_iops_string": {
                                    "$regexFind": {
                                        "input": "$msg",
                                        "regex": "sequential_write_iops\\s*=\\s*([\\d\\.]+)"
                                    }
                                },
                                "write_bw_string": {
                                    "$regexFind": {
                                        "input": "$msg",
                                        "regex": "sequential_write_bw\\s*=\\s*([\\d\\.]+)"
                                    }
                                }
                            }
                        },
                        # Stage 10
                        {
                            "$project": {
                                "write_pattern": 1,
                                "block_size": 1,
                                "read_iops": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$read_iops_string.captures",
                                                0
                                            ]
                                        },
                                        "to": "double",
                                        "onError": None,
                                        "onNull": None
                                    }
                                },
                                "read_bw": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$read_bw_string.captures",
                                                0
                                            ]
                                        },
                                        "to": "double",
                                        "onError": None,
                                        "onNull": None
                                    }
                                },
                                "write_iops": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$write_iops_string.captures",
                                                0
                                            ]
                                        },
                                        "to": "double",
                                        "onError": None,
                                        "onNull": None
                                    }
                                },
                                "write_bw": {
                                    "$convert": {
                                        "input": {
                                            "$arrayElemAt": [
                                                "$write_bw_string.captures",
                                                0
                                            ]
                                        },
                                        "to": "double",
                                        "onError": None,
                                        "onNull": None
                                    }
                                }
                            }
                        },
                        # Stage 11
                        {
                            "$group": {
                                "_id": {
                                    "write_pattern": "$write_pattern",
                                    "block_size": "$block_size"
                                },
                                "avg_read_iops": { "$avg": "$read_iops" },
                                "avg_read_bw": { "$avg": "$read_bw" },
                                "std_dev_read_iops": { "$stdDevPop": "$read_iops" },
                                "avg_write_iops": { "$avg": "$write_iops" },
                                "avg_write_bw": { "$avg": "$write_bw" },
                                "std_dev_write_iops": { "$stdDevPop": "$write_iops" }
                            }
                        }
                    ]

        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.critical(f"Error performing aggregation: {e}")
            return None
        
    def aggregate_ramp_metrics(self, write_pattern, ramp_times):
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "report.tests.keywords": 1,
                    "report.tests.call.log.msg": 1
                }
            },
            { "$unwind": { "path": "$report.tests" } },
            { "$unwind": { "path": "$report.tests.keywords" } },
            {
                "$match": {
                    "report.tests.keywords": {
                        "$regex": "test_run_io_operation"
                    }
                }
            },
            { "$unwind": { "path": "$report.tests.call" } },
            { "$unwind": { "path": "$report.tests.call.log" } },
            {
                "$project": {
                    "msg": "$report.tests.call.log.msg",
                    "write_pattern_string": {
                        "$regexFind": {
                            "input": "$report.tests.keywords",
                            # "regex": "test_run_io_operation\\[(\\d+)-(\\d+)\\]"
                            "regex": "test_run_io_operation\\[(\\d+)-(\\d+)"
                        }
                    }
                }
            },
            {
                "$project": {
                    "msg": 1,
                    "write_pattern": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_pattern_string.captures",
                                    0
                                ]
                            },
                            "to": "int",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "ramp_times": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_pattern_string.captures",
                                    1
                                ]
                            },
                            "to": "int",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            {
                "$project": {
                    "write_pattern": 1,
                    "ramp_times": 1,
                    "read_iops_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "ramp_read_iops = (\\d+.\\d+)"
                        }
                    },
                    "read_bw_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "ramp_read_bw = (\\d+.\\d+)"
                        }
                    },
                    "write_iops_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "ramp_write_iops = (\\d+.\\d+)"
                        }
                    },
                    "write_bw_string": {
                        "$regexFind": {
                            "input": "$msg",
                            "regex": "ramp_write_bw = (\\d+.\\d+)"
                        }
                    }
                }
            },
            {
                "$project": {
                    "write_pattern": 1,
                    "ramp_times": 1,
                    "read_iops": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$read_iops_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "read_bw": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$read_bw_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "write_iops": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_iops_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                    "write_bw": {
                        "$convert": {
                            "input": {
                                "$arrayElemAt": [
                                    "$write_bw_string.captures",
                                    0
                                ]
                            },
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            { "$match": { "write_pattern": write_pattern ,
                         "ramp_times": ramp_times
                        } 
            },
            {
                "$group": {
                    "_id": {
                        "write_pattern": "$write_pattern",
                        "ramp_times": "$ramp_times"
                    },
                    "avg_read_iops": { "$avg": "$read_iops" },
                    "avg_read_bw": { "$avg": "$read_bw" },
                    "std_dev_read_iops": {"$stdDevPop": "$read_iops"},
                    "avg_write_iops": { "$avg": "$write_iops" },
                    "avg_write_bw": { "$avg": "$write_bw" },
                    "std_dev_write_iops": {"$stdDevPop": "$write_iops"}
                }
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.critical(f"Error performing aggregation: {e}")
            return None