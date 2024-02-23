import os
import dotenv
 
from deploy.helpers.run_helper import get_stack_qualifier
 
 
dotenv.load_dotenv()
 
ENVIRONMENT = os.getenv("ENVIRONMENT")
S3_BUCKET_FOR_SAM = os.getenv("BUCKET_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
 
WG_MAIIL_FOR_SENDING = "abhi22hada@gmail.com"
RECEIVER_MAILS = ["udbhavmani20@gmail.com","naugaria.ar.6@gmail.com"]

EMAILS = []
EMAILS.append(WG_MAIIL_FOR_SENDING)
EMAILS += RECEIVER_MAILS


APPLICATION_NAME = "wg-visitor-mgmt-system"
SAM_STACK_NAME = f"{get_stack_qualifier('api-gateway')}"
BUCKET_NAME = f"{get_stack_qualifier('static-content')}"
USER_POOL_NAME = f"{get_stack_qualifier('user-pool')}"
USER_POOL_CLIENT_NAME = f"{get_stack_qualifier('user-pool-client')}"
TABLE_NAME = f"{get_stack_qualifier('database')}"
ROLE_NAME = f"{get_stack_qualifier('lambda-role-common')}"
SENDER_EMAIL = WG_MAIIL_FOR_SENDING
RECIPIENT_EMAIL = ",".join(RECEIVER_MAILS)
