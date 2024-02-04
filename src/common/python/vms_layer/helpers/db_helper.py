import boto3
from botocore.exceptions import ClientError

class DBHelper:
    """Helper class for DynamoDB operations"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def create_item(self, item):
        """Create an item in the table"""
        try:
            response = self.table.put_item(Item=item)
            return response
        except ClientError as e:
            print(f"Error creating item: {e}")
            return None

    def get_item(self, key):
        """Get an item from the table"""
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None

    def update_item(self, key, update_expression, expression_attribute_values):
        """Update an item in the table"""
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW",
            )
            return response
        except ClientError as e:
            print(f"Error updating item: {e}")
            return None

    def delete_item(self, key):
        """Delete an item from the table"""
        try:
            response = self.table.delete_item(Key=key)
            return response
        except ClientError as e:
            print(f"Error deleting item: {e}")
            return None

    def query_items(
        self,
        key_condition_expression,
        expression_attribute_values,
        page_size=10,
        starting_token=None,
        filter_expression=None,
        expression_attribute_names=None,
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

        try:
            response = self.table.query(**query_params)
            return response
        except ClientError as e:
            print(f"Error querying items: {e}")
            return None

    def batch_get_items(self, keys):
        """Batch query items from the table"""
        try:
            response = self.table.batch_get_item(Keys=keys)
            return response
        except ClientError as e:
            print(f"Error batch getting items: {e}")
            return None
