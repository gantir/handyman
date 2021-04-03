import os
import sys
import urllib
import zipfile
from io import BytesIO

import boto3


def get_lambda_functions_code_url():

    client = boto3.client("lambda")

    lambda_functions = [n["FunctionName"] for n in client.list_functions()["Functions"]]

    functions_code_url = []

    for fn_name in lambda_functions:
        fn_code = client.get_function(FunctionName=fn_name)["Code"]
        fn_code["FunctionName"] = fn_name
        functions_code_url.append(fn_code)

    return functions_code_url


def download_lambda_function_code(fn_name, fn_code_link, dir_path):

    function_path = os.path.join(dir_path, fn_name)
    if not os.path.exists(function_path):
        os.mkdir(function_path)

    with urlopen(fn_code_link) as lambda_extract:
        with zipfile.ZipFile(BytesIO(lambda_extract.read())) as zfile:
            zfile.extractall(function_path)


if __name__ == "__main__":
    inp = sys.argv[1:]
    print("Destination folder {}".format(inp))
    if inp and os.path.exists(inp[0]):
        dest = os.path.abspath(inp[0])
        fc = get_lambda_functions_code_url()
        print("There are {} lambda functions".format(len(fc)))
        for i, f in enumerat(fc):
            print("Downloading Lambda function {} {}".format(i, f["FunctionName"]))
            download_lambda_function_code(f["FunctionName"], f["Location"], dest)
    else:
        print("Destination folder doesn't exist")