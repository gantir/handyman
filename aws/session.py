# Credits: This code is inspired from this article: https://advancedweb.hu/aws-how-to-secure-access-keys-with-mfa/

import boto3
import os
import subprocess
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

def get_shell():
    ppid = os.getppid()
    out = subprocess.check_output(['ps', '-o', 'comm', '-p', str(ppid)])
    return out.splitlines()[-1].decode("utf-8").strip("-")

def set_env_access(access_keys):
    try:
        env = {}
        env["AWS_ACCESS_KEY_ID"] = access_keys["AccessKeyId"]
        env["AWS_SECRET_ACCESS_KEY"] = access_keys["SecretAccessKey"]
        env["AWS_SESSION_TOKEN"] = access_keys["SessionToken"]
        shell = get_shell()

        env_list = [f"export {k}={v}" for k,v in env.items()]
        if shell == "fish":
            env_list = [f"set -gx {k} {v}" for k,v in env.items()]

        return "\n".join(env_list)

    except Exception as e:
        print(e)
        raise e

def unset_env():
    env_var = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]
    shell = get_shell()

    env_list = [f"unset {var}" for var in env_var]
    if shell == "fish":
        env_list = [f"set -e {var}" for var in env_var]

    return "\n".join(env_list)

if __name__ == "__main__":
    param = sys.argv[1:]
    if len(param) > 0:
        if param[0].lower() == "unset":
            unset_env()
        else:
            mfa_serial_number = get_serial_number()
            access_keys = get_access_keys(mfa_serial_number, param[0])
            print(set_env_access(access_keys), file=sys.stdout)
    else:
        print("Usage \n python session.py 123456 # for getting session token. \n python session.py unset for unsetting session token")
