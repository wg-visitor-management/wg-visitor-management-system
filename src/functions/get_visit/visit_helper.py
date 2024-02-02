import os
import time
import base64
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


class VisitHelper:
    def __init__(self):
        pass

    def get_filtered_visits_date_range(
        self,
        start_date,
        end_date,
        organization=None,
        approver=None,
    ):
        quarters = extract_quarters_from_date_range(start_date, end_date)
        start_date_formatted = date_to_epoch(start_date)
        end_date_formatted = date_to_epoch(end_date)
        logger.debug(f"Quarters: {quarters}, start_date: {start_date}, end_date: {end_date}")

        response = []
        db_helper = DBHelper(os.environ["DynamoDBTableName"])

        for quarter in quarters:
            items = self.query_items_with_filters(
                db_helper,
                quarter,
                start_date_formatted,
                end_date_formatted,
                organization,
                approver,
            )
            response += items
        logger.debug(f"Response: {response}")

        for item in response:
            item.pop("PK")
            item.pop("SK")
            item["date"] = epoch_to_date(int(item["check_in_time"])).split("T")[0]
            item["check_in_time"] = epoch_to_date(int(item["check_in_time"])).split("T")[1]
        return response

    def query_items_with_filters(
        self,
        db_helper,
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
            filter_expression = "approved_by = :approver"
            expression_attribute_values[":approver"] = approver

        return self.query_items(
            db_helper,
            key_condition_expression="PK = :PK AND SK BETWEEN :start_date AND :end_date",
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )

    def get_visits_by_visitor_id(self, visitor_id, pageSize=50, nextPageToken=None):
        """Get the visits of a visitor by visitor id"""
        db_helper = DBHelper(os.environ["DynamoDBTableName"])
        decoded_id = base64_to_string(visitor_id)
        timestamp = decoded_id
        formatted_timestamp = epoch_to_date(int(timestamp))
        time_now = current_time_epoch()
        time_now_formatted = epoch_to_date(time_now)
        quarters = extract_quarters_from_date_range(formatted_timestamp, time_now_formatted)
        response = []
        for quarter in quarters:
            items = self.query_items(
                db_helper,
                key_condition_expression="PK = :PK AND begins_with(SK, :SK)",
                expression_attribute_values={
                    ":PK": f"visit#{quarter}",
                    ":SK": f"visit#{timestamp}",
                },
            )
            response += items

        for item in response:
            item.pop("PK")
            item.pop("SK")
            logger.debug(f"Item: {item}")
            item["date"] = epoch_to_date(int(item["check_in_time"])).split("T")[0]
            item["check_in_time"] = epoch_to_date(int(item["check_in_time"])).split("T")[1]
            
        logger.debug(f"Response: {response}")
        return response

    def query_items(
        self,
        db_helper,
        key_condition_expression,
        filter_expression=None,
        expression_attribute_values=None,
    ):
        """Query items from the table"""
        items = []
        response = db_helper.query_items(
            key_condition_expression=key_condition_expression,
            page_size=int(10),
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )
        items += response["Items"]
        logger.debug(f"Items: {items}")
        while "LastEvaluatedKey" in response:
            response = db_helper.query_items(
                key_condition_expression=key_condition_expression,
                page_size=int(10),
                starting_token=response["LastEvaluatedKey"],
                filter_expression=filter_expression,
                expression_attribute_values=expression_attribute_values,
            )
            items += response["Items"]

        logger.debug(f"Items Q: {items}")
        return items
