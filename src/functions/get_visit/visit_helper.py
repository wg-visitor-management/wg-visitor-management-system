"""
This module contains the VisitHelper class
that is responsible for getting the visits from the database
with some filters.
"""
 
from body_parser import BodyParser
 
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    date_to_epoch,
    epoch_to_date,
)
 
logger = get_logger("GET /visit")
db_helper = DBHelper()
 
 
class VisitHelper:
    """
    This class is used to get the visits from the database with some filters.
    """
 
    def __init__(self):
        pass
 
    def get_filtered_visits_date_range(
        self,
        start_date,
        end_date,
        organization=None,
        approver=None,
    ):
        """Get the visits from the database with some filters like start and end date"""
        quarters = extract_quarters_from_date_range(start_date, end_date)
        start_date_formatted = date_to_epoch(start_date)
        end_date_formatted = date_to_epoch(end_date)
 
        response = []
        for quarter in quarters:
            items = self.query_items_with_filters(
                quarter,
                start_date_formatted,
                end_date_formatted,
                organization,
                approver,
            )
            response += items
        logger.debug({"Response %s": response})
        response_body = BodyParser(response).parse_response()
        logger.info({"Response %s": response_body})
        return response_body
 
    def query_items_with_filters(
        self,
        quarter,
        start_date_formatted,
        end_date_formatted,
        organization=None,
        approver=None,
    ):
        """Query items from the table with filters"""
        filter_expression = None
        expression_attribute_values = {
            ":PK": f"history#{quarter}",
            ":start_date": f"history#{start_date_formatted}",
            ":end_date": f"history#{end_date_formatted}",
        }
        if organization:
            filter_expression = "organization = :organization"
            expression_attribute_values[":organization"] = organization
        elif approver:
            filter_expression = "approvedBy = :approver"
            expression_attribute_values[":approver"] = approver
 
        response = self.query_items(
            key_condition_expression="PK = :PK AND SK BETWEEN :start_date AND :end_date",
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )
        logger.info({"Response %s": response})
        return response
 
    def get_visits_by_visitor_id(self, visitor_id):
        """Get the visits of a visitor by visitor id"""
        decoded_id = base64_to_string(visitor_id)
        timestamp = decoded_id
        formatted_timestamp = epoch_to_date(int(timestamp))
        time_now = current_time_epoch()
        time_now_formatted = epoch_to_date(time_now)
        quarters = extract_quarters_from_date_range(
            formatted_timestamp, time_now_formatted
        )
        response = []
        for quarter in quarters:
            items = self.query_items(
                key_condition_expression="PK = :PK AND begins_with(SK, :SK)",
                expression_attribute_values={
                    ":PK": f"visit#{quarter}",
                    ":SK": f"visit#{timestamp}",
                },
            )
            response += items
        response_body = BodyParser(response).parse_response()
        return response_body
 
    def query_items(
        self,
        key_condition_expression,
        filter_expression=None,
        expression_attribute_values=None,
    ):
        """Query items from the table"""
        items = []
        response = db_helper.query_items(
            key_condition_expression=key_condition_expression,
            page_size=int(30),
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )
        items += response["Items"]
        while "LastEvaluatedKey" in response:
            response = db_helper.query_items(
                key_condition_expression=key_condition_expression,
                page_size=int(30),
                starting_token=response["LastEvaluatedKey"],
                filter_expression=filter_expression,
                expression_attribute_values=expression_attribute_values,
            )
            items += response["Items"]
 
        logger.debug("Items %s", items)
        return items