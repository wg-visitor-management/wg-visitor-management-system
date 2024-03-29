import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.getenv("DynamoDBTableName")
class DBHelper:
    """Helper class for DynamoDB operations"""

    def __init__(self):
        self.table_name = TABLE_NAME
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(TABLE_NAME)

    def create_item(self, item):
        """Create an item in the table"""
        try:
            response = self.table.put_item(Item=item)
            return response
        except ClientError as error:
            return error

    def get_item(self, key):
        """Get an item from the table"""
        try:
            response = self.table.get_item(Key=key, ConsistentRead=True)
            return response.get("Item")
        except ClientError as error:
            return error

    def update_item(self, key, update_expression, expression_attribute_values):
        """Update an item in the table"""
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )
            return response
        except ClientError as error:
            return error

    def delete_item(self, key):
        """Delete an item from the table"""
        try:
            response = self.table.delete_item(Key=key)
            return response
        except ClientError as error:
            return error

    def query_items(
        self,
        key_condition_expression,
        expression_attribute_values,
        page_size=10,
        starting_token=None,
        filter_expression=None,
        expression_attribute_names=None,
        consistent_read=False
    ):
        """Query items from the table"""
        query_params = {
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "Limit": page_size,
        }

        if filter_expression:
            query_params["FilterExpression"] = filter_expression

        if expression_attribute_names:
            query_params["ExpressionAttributeNames"] = expression_attribute_names

        if starting_token:
            query_params["ExclusiveStartKey"] = starting_token
        
        if consistent_read:
            query_params["ConsistentRead"] = consistent_read

        try:
            response = self.table.query(**query_params)
            return response
        except ClientError as error:
            return error

    def batch_get_items(self, keys):
        """Batch query items from the table"""
        try:
            response = self.table.batch_get_item(Keys=keys)
            return response
        except ClientError as error:
            return error
