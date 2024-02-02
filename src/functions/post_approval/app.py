import base64
import json
import os
import boto3
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    epoch_to_date,
    current_time_epoch,
)
from vms_layer.config.schemas.approval_schema import post_approval_schema

client = boto3.client("ses")
logger = get_logger("POST /approval")
db_helper = DBHelper(os.environ.get("DynamoDBTableName"))


@handle_errors
@rbac
@validate_schema(post_approval_schema)
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    logger.debug(f"Received event: {event}")

    visit_id = body.get("visit_id")
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id, timestamp = decoded_visit_id.split("#")
    current_time = current_time_epoch()
    current_quarter = extract_quarters_from_date_range(
        epoch_to_date(current_time), epoch_to_date(current_time)
    )[0]

    update_database_items(current_quarter, decoded_visit_id, visitor_id, timestamp)
    send_approval_email(visitor_id)
    logger.info(f"Approval request sent successfully")
    return ParseResponse(
        {"message": "Approval request sent successfully"}, 200
    ).return_response()


def update_database_items(current_quarter, decoded_visit_id, visitor_id, timestamp):
    logger.info(f"Updating visit {decoded_visit_id} with approval status")
    db_helper.update_item(
        key={"PK": f"visit#{current_quarter}", "SK": f"visit#{decoded_visit_id}"},
        update_expression="SET approval_status = :approved",
        expression_attribute_values={":approved": "pending"},
    )

    db_helper.update_item(
        key={
            "PK": f"history#{current_quarter}",
            "SK": f"history#{timestamp}#{visitor_id}",
        },
        update_expression="SET approval_status = :approved",
        expression_attribute_values={":approved": "pending"},
    )


def send_approval_email(visitor_id):
    email_content = {
        "Source": "udbhavmani20@gmail.com",
        "Destination": {"ToAddresses": ["udbhavmani20@gmail.com"]},
        "Message": {
            "Body": {
                "Html": {
                    "Charset": "UTF-8",
                    "Data": get_email_html(visitor_id),
                },
            },
            "Subject": {"Charset": "UTF-8", "Data": "Visit Approval"},
        },
    }

    client.send_email(**email_content)


def get_email_html(visitor_id):
    return """
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <meta http-equiv="x-ua-compatible" content="ie=edge">
                <title>Email Confirmation</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style type="text/css">
                @media screen {
                    @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 400;
                    src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
                    }
                    @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 700;
                    src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
                    }
                }
                body,
                table,
                td,
                a {
                    -ms-text-size-adjust: 100%;
                    -webkit-text-size-adjust: 100%;
                }
                table,
                td {
                    mso-table-rspace: 0pt;
                    mso-table-lspace: 0pt;
                }
                img {
                    -ms-interpolation-mode: bicubic;
                }
                a[x-apple-data-detectors] {
                    font-family: inherit !important;
                    font-size: inherit !important;
                    font-weight: inherit !important;
                    line-height: inherit !important;
                    color: inherit !important;
                    text-decoration: none !important;
                }
                div[style*="margin: 16px 0;"] {
                    margin: 0 !important;
                }
                body {
                    width: 100% !important;
                    height: 100% !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }
                table {
                    border-collapse: collapse !important;
                }
                a {
                    color: #1a82e2;
                }
                img {
                    height: auto;
                    line-height: 100%;
                    text-decoration: none;
                    border: 0;
                    outline: none;
                }
                </style>
                </head>
                <body style="background-color: #e9ecef;">
                <div class="preheader" style="display: none; max-width: 0; max-height: 0; overflow: hidden; font-size: 1px; line-height: 1px; color: #fff; opacity: 0;">
                    A visitor needs your approval
                </div>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                    <td align="center" bgcolor="#e9ecef">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="center" valign="top" style="padding: 36px 24px;">
                            <a href="#" target="_blank" style="display: inline-block;">
                            </a>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td align="center" bgcolor="#e9ecef">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="left" bgcolor="#ffffff" style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
                            <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;">A visitor has arrived</h1>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td align="center" bgcolor="#e9ecef">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="left" bgcolor="#ffffff">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                <td align="center" bgcolor="#ffffff" style="padding: 12px;">
                                    <table border="0" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" bgcolor="#1a82e2" style="border-radius: 6px;">
                                        <a href="" target="_blank" style="display: inline-block; border:10px; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;">Approve</a>
                                        </td>
                                        <td align="center" bgcolor="red" style="border-radius: 6px;">
                                        <a href="" target="_blank" style="display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;">Reject</a>
                                        </td>
                                    </tr>
                                    </table>
                                </td>
                                </tr>
                            </table>
                            </td>
                        </tr>
                        <tr>
                            <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                            <p style="margin: 0;">{}</p>
                            </td>
                        </tr>
                        <tr>
                            <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px; border-bottom: 3px solid #d4dadf">
                            <p style="margin: 0;">Cheers,<br> Paste</p>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td align="center" bgcolor="#e9ecef" style="padding: 24px;">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="center" bgcolor="#e9ecef" style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                            <p style="margin: 0;">You received this email because we received a request for [type_of_action] for your account. If you didn't request [type_of_action] you can safely delete this email.</p>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" bgcolor="#e9ecef" style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                            <p style="margin: 0;">To stop receiving these emails, you can at any time.</p>
                            <p style="margin: 0;">Paste 1234 S. Broadway St. City, State 12345</p>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                </table>
                </body>
                </html>


                """
