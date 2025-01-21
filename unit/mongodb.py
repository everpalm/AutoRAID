# Contents of unit/mongodb.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
from pymongo import MongoClient, errors
from pymongo import DESCENDING
from unit.log_handler import get_logger

# logger = logging.getLogger(__name__)
logger = get_logger(__name__, logging.INFO)

# PROJECT_PATH = "/home/pi/Projects/AutoRAID"


class MongoDB(object):
    """
    A class for interacting with a MongoDB database.

    This class provides methods to perform CRUD (Create, Read, Update, Delete)
    operations on a MongoDB collection, as well as methods to aggregate data
    for metrics related to I/O operations.

    Attributes:
        client (MongoClient): The MongoDB client instance.
        db (Database): The MongoDB database instance.
        collection (Collection): The MongoDB collection instance.
    """
    def __init__(self, host, port, db_name, collection_name):
        """
        Initializes the MongoDB class with a connection to the specified
        MongoDB database and collection.

        Args:
            host (str): The hostname or IP address of the MongoDB server.
            port (int): The port number on which the MongoDB server is
            listening.
            db_name (str): The name of the database to connect to.
            collection_name (str): The name of the collection within the
            database.

        Raises:
            PyMongoError: If there is an error connecting to the MongoDB
            server.
        """
        self.client = MongoClient(f'mongodb://{host}:{port}')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def write_log_and_report(self, log_path, report_path):
        """
        Writes log and report data from files to the MongoDB collection.

        Reads log data from a text file and report data from a JSON file, and
        inserts them into the MongoDB collection as a single document.

        Args:
            log_path (str): The file path to the log file.
            report_path (str): The file path to the report JSON file.

        Raises:
            FileNotFoundError: If the specified log or report file is not
            found.
            IOError: If there is an error reading the log file.
            JSONDecodeError: If the report file cannot be decoded as JSON.
            PyMongoError: If there is an error inserting the document into
            MongoDB.
        """
        try:
            with open(log_path, 'r', encoding='iso-8859-1') as log_file:
                log_data = log_file.read()
        except UnicodeDecodeError as e:
            logger.error("Decoding error at position %s: %s", e.start,
                         e.reason)
            raise
        except FileNotFoundError:
            logger.error("Error: The file %s was not found", log_path)
            return
        except IOError as e:
            logger.critical("Error reading %s: %s", log_path, e)
            return

        try:
            with open(report_path, 'r') as report_file:
                report_data = json.load(report_file)
        except FileNotFoundError:
            logger.error("Error: The file %s was not found", report_path)
            return
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from %s: %s", report_path, e)
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
        """
        Reads all documents from the MongoDB collection and writes them to a
        JSON file.

        Args:
            result_path (str): The file path to write the results to (default:
            'result.json').

        Raises:
            PyMongoError: If there is an error reading from MongoDB.
            IOError: If there is an error writing to the result file.
        """
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
        """
        Updates a document in the MongoDB collection based on the given filter
        query.

        Args:
            filter_query (dict): The query to filter the document that needs to
            be updated.
            update_values (dict): The values to update in the document.

        Raises:
            PyMongoError: If there is an error updating the document in
            MongoDB.
        """
        try:
            result = self.collection.update_one(filter_query,
                                                {'$set': update_values})
            if result.matched_count:
                logger.debug("Document updated successfully: %s "
                             "document(s) modified.", result.modified_count)
            else:
                logger.debug("No document matches the given query.")
        except errors.PyMongoError as e:
            logger.critical(f"Error updating document: {e}")

    def delete_document(self, filter_query):
        """
        Deletes a document from the MongoDB collection based on the given
        filter query.

        Args:
            filter_query (dict): The query to filter the document that needs to
            be deleted.

        Raises:
            PyMongoError: If there is an error deleting the document from
            MongoDB.
        """
        try:
            result = self.collection.delete_one(filter_query)
            if result.deleted_count:
                logger.debug("Document deleted successfully: %s "
                             "document(s) deleted.", result.deleted_count)
            else:
                logger.debug("No document matches the given query.")
        except errors.PyMongoError as e:
            logger.error(f"Error deleting document: {e}")

    def find_document(self, filter_query):
        """
        Finds a single document in the MongoDB collection based on the given
        filter query.

        Args:
            filter_query (dict): The query to filter the document.

        Returns:
            dict or None: The document if found, otherwise None.

        Raises:
            PyMongoError: If there is an error finding the document in MongoDB.
        """
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
        """
        Aggregates random I/O metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for random IOPS and bandwidth
        based on the write pattern and I/O depth.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.,
            50 for 50% writes).
            io_depth (int): The I/O depth to filter the metrics.

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_rdn_perf.json', 'r',
                      encoding='us-ascii') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline "
                            "configuration: %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "write_pattern" in stage["$match"]:
                stage["$match"]["write_pattern"]["$eq"] = write_pattern
            if "$match" in stage and "io_depth" in stage["$match"]:
                stage["$match"]["io_depth"]["$eq"] = io_depth
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

    def aggregate_sequential_metrics(self, write_pattern, block_size):
        """
        Aggregates sequential I/O metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for sequential IOPS and
        bandwidth based on the write pattern and block size.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.,
            50 for 50% writes).
            io_depth (int): The I/O depth to filter the metrics.

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_seq_perf.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline "
                            "configuration: %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "write_pattern" in stage["$match"]:
                stage["$match"]["write_pattern"]["$eq"] = write_pattern
            if "$match" in stage and "block_size" in stage["$match"]:
                stage["$match"]["block_size"]["$eq"] = block_size

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
        """
        Aggregates ramp I/O metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for ramp IOPS and bandwidth
        based on the write pattern and ramp times.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.
            ,50 for 50% writes).
            ramp_times (int): The ramp times to filter the metrics.

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_ramp_times.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline "
                            "configuration: %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "write_pattern" in stage["$match"]:
                stage["$match"]["write_pattern"]["$eq"] = write_pattern
            if "$match" in stage and "ramp_times" in stage["$match"]:
                stage["$match"]["ramp_times"]["$eq"] = ramp_times

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

    def aggregate_stress_metrics(self, write_pattern, iodepth):
        """
        Aggregates I/O stress metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for random IOPS and bandwidth
        based on the write pattern and I/O depth.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.
            , 50 for 50% writes).
            io_depth (int): The I/O depth to filter the metrics.

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_stress.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline configuration:"
                            " %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "write_pattern" in stage["$match"]:
                stage["$match"]["write_pattern"]["$eq"] = write_pattern
            if "$match" in stage and "io_depth" in stage["$match"]:
                stage["$match"]["io_depth"]["$eq"] = iodepth

        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.error("Error performing aggregation: %s", e)
            return None

    def aggregate_best_ramp_time(self):
        """
        Aggregates best ramp time from the MongoDB collection.
        """
        try:
            with open('config/pipeline_best_ramp_time.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline "
                            "configuration: %s", e)
            return None

        # for stage in pipeline:
        #     if "$match" in stage and "write_pattern" in stage["$match"]:
        #         stage["$match"]["write_pattern"]["$eq"] = write_pattern

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

    def aggregate_oltp_metrics(self, iodepth: str):
        """
        Aggregates OLTP stress metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for random IOPS and bandwidth
        based on the write pattern and I/O depth.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.
            , 50 for 50% writes).
            io_depth (int): The I/O depth to filter the metrics.

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_oltp.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline configuration:"
                            " %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "iodepth" in stage["$match"]:
                stage["$match"]["iodepth"]["$eq"] = iodepth

        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.error("Error performing aggregation: %s", e)
            return None

    def aggregate_olap_metrics(self, write_pattern):
        """
        Aggregates OLAP stress metrics from the MongoDB collection.

        The aggregation pipeline processes documents to extract and compute
        average and standard deviation metrics for random IOPS and bandwidth
        based on the write pattern and I/O depth.

        Args:
            write_pattern (int): The write pattern to filter the metrics (e.g.
            , 50 for 50% writes).

        Returns:
            dict or None: A dictionary containing the aggregated metrics, or
            None if no data is found.

        Raises:
            PyMongoError: If there is an error performing the aggregation in
            MongoDB.
        """
        try:
            with open('config/pipeline_olap.json', 'r',
                      encoding='utf-8') as file:
                pipeline = json.load(file)
        except FileNotFoundError:
            logger.error("Pipeline configuration file not found.")
            return None
        except json.JSONDecodeError as e:
            logger.critical("Error decoding JSON from pipeline configuration:"
                            " %s", e)
            return None

        # Update the pipeline with the specific filter values
        for stage in pipeline:
            if "$match" in stage and "write_pattern" in stage["$match"]:
                stage["$match"]["write_pattern"]["$eq"] = write_pattern

        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                return result[0]
            else:
                logger.error("No data found for aggregation.")
                return None
        except errors.PyMongoError as e:
            logger.error("Error performing aggregation: %s", e)
            return None
