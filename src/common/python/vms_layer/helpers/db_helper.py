"""Helper class for DynamoDB operations"""
import boto3
 
 
class DBHelper:
    """Helper class for DynamoDB operations"""
 
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def create_item(self, item):
        """Create an item in the table"""
        response = self.table.put_item(Item=item)
        return response

    def get_item(self, key):
        """Get an item from the table"""
        response = self.table.get_item(Key=key)
        return response.get("Item")
 
    def update_item(self, key, update_expression, expression_attribute_values):
        """Update an item in the table"""
        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )
        return response

    def delete_item(self, key):
        """Delete an item from the table"""
        response = self.table.delete_item(Key=key)
        return response
 
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
 
        response = self.table.query(**query_params)
 
        return response
 
    def batch_get_items(self, keys):
        """Batch query items from the table"""
        response = self.table.batch_get_item(Keys=keys)
        return response