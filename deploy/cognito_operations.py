import boto3

client = boto3.client('cognito-idp')
client_id = "298bm48gainnbe547nbo18o48p"
userpool_id = "ap-south-1_LlDNNaRJa"

def initiate_auth(username, password):
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
    except client.exceptions.NotAuthorizedException:
        print("Incorrect username or password")
        return
    print(response)
    return response

def set_new_password(session, username, new_password):
    
    response = client.respond_to_auth_challenge(
        ClientId=client_id,
        ChallengeName='NEW_PASSWORD_REQUIRED',
        ChallengeResponses={
            'USERNAME': username,
            'NEW_PASSWORD': new_password
        },
        Session=session
    )
    print(response)
    return response

def associate_software_token(access_token):
    response = client.associate_software_token(
        AccessToken=access_token
    )
    print(response)

    return response

def verify_software_token(access_token, code):
    response = client.verify_software_token(
        AccessToken=access_token,
        UserCode=code
    )
    print(response)

    return response

def respond_to_auth_challenge(access_token, username, code):
    response = client.respond_to_auth_challenge(
        ClientId=client_id,
        ChallengeName='MFA_SETUP',
        ChallengeResponses={
            'USERNAME': username,
            'SOFTWARE_TOKEN_MFA_CODE': code
        },
        AccessToken=access_token
    )
    print(response)

    return response

def admin_add_user_to_group(username, group_name):
    try:
        response = client.admin_add_user_to_group(
            UserPoolId= userpool_id,
            Username=username,
            GroupName=group_name)
    except client.exceptions.UserNotFoundException:
        print("User not found")
        return
    
    print(response)
    return response

def admin_create_group(group_name, description):
    try:
        response = client.create_group(
            GroupName=group_name,
            UserPoolId=userpool_id,
            Description=description
        )
    except client.exceptions.GroupExistsException:
        print("Group already exists")
        return
    return response

def create_user(username, password, name):
    try:
        response = client.sign_up(
            ClientId=client_id,
            Username = username,
            Password = password,
            UserAttributes=[
                {
                    'Name': 'name',
                    'Value': name
                }]
        )
        client.admin_confirm_sign_up(
            UserPoolId=userpool_id,
            Username=username
        )
    except client.exceptions.UsernameExistsException:
        print("User already exists")
        return
    print(response)
    return response

def confirm_sign_up(username, code):
    response = client.confirm_sign_up(
        ClientId=client_id,
        Username=username,
        ConfirmationCode=code
    )
    print(response)
    return response

def verify_email_address(username):
    try:
        response = client.admin_update_user_attributes(
            UserPoolId=userpool_id,
            Username=username,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
        )
    except client.exceptions.UserNotFoundException:
        print("User not found")
        return
    print(response)
    return response


def create_user_add_to_group(name, username, password, group_name):
    create_user(username, password, name)
    admin_create_group(group_name, "Group for testing")
    admin_add_user_to_group(username, group_name)
    verify_email_address(username)
    initiate_auth(username, password)

if __name__ == "__main__":
    create_user_add_to_group("Kittu", "cod12321@gmail.com", "AWSpass123!", "admin")
