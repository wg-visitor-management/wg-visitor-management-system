import os
import dotenv

from deploy.run_helper import get_stack_qualifier


dotenv.load_dotenv()
 
ADMIN_EMAIL = [os.getenv("ADMIN_EMAIL")]
ENVIRONMENT = os.getenv("ENVIRONMENT")
S3_BUCKET_FOR_SAM = os.getenv("BUCKET_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")

APPLICATION_NAME = "wg-visitor-mgmt-system"
SAM_STACK_NAME = f"{get_stack_qualifier('api-gateway')}"
BUCKET_NAME = f"{get_stack_qualifier('static-content')}"
USER_POOL_NAME = f"{get_stack_qualifier('user-pool')}"
USER_POOL_CLIENT_NAME = f"{get_stack_qualifier('user-pool-client')}"
TABLE_NAME = f"{get_stack_qualifier('database')}"
ROLE_NAME = f"{get_stack_qualifier('lambda-role-common')}"
SENDER_EMAIL = ADMIN_EMAIL
RECIPIENT_EMAIL = ADMIN_EMAIL
