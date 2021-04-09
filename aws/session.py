import boto3
import os
import sys

iam = boto3.client('iam')
sts = boto3.client('sts')

def get_serial_number():
    try:
        user_name = sts.get_caller_identity()["Arn"].split("/")[1]
        mfa_serial_number = iam.list_mfa_devices(UserName=user_name)["MFADevices"][0]["SerialNumber"]
        return mfa_serial_number
    except Exception as e:
        print(e)
        raise e


def get_access_keys(serial_number, token_code):
    try:
        return sts.get_session_token(
            SerialNumber = serial_number,
            TokenCode = token_code
        )["Credentials"]

    except Exception as e:
        print(e)
        raise e

def set_env_access(access_keys):
    try:
        os.environ["AWS_ACCESS_KEY_ID"] = access_keys["AccessKeyId"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = access_keys["SecretAccessKey"]
        os.environ["AWS_Session_Token"] = access_keys["SessionToken"]
    except Exception as e:
        print(e)
        raise e

if __name__ == "__main__":
    token_code = sys.argv[1:]
    mfa_serial_number = get_serial_number()
    if token_code:
        access_keys = get_access_keys(serial_number, token_code)
        set_env_access(access_keys)
    else:
        print("Token Code is Mandatory")
