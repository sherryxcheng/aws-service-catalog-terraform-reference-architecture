from pathlib import Path
import urllib3
import json
import os


def send(event, responseStatus, responseData, noEcho=False):
    http = urllib3.PoolManager()
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream for CodeBuild: ' + os.environ['CODEBUILD_BUILD_ID']
    responseBody['PhysicalResourceId'] = event['StackId'] + event['ResourceType']
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        
        response = http.request('PUT',responseUrl,body=json_responseBody.encode('utf-8'),headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))


if __name__ == '__main__':
    try:
        event = json.loads(os.environ['event'])
        data = dict()
        status = "SUCCESS"

        # AWS CodeBuild Environment variable CODEBUILD_BUILD_SUCCEEDING will be set to 0 if failed, otherwise is 1
        if str(os.environ['CODEBUILD_BUILD_SUCCEEDING']) == str(0):
            status = "FAILED"
        tf_output = ''
        tf_output_file = Path("/tmp/tf_output.txt")
        if tf_output_file.is_file():
            with open(tf_output_file, 'r') as file:
                tf_output = file.read()

            data['TF_OUTPUT'] = tf_output
        
        send(event, status, data)
    except Exception as e:
        send(event, 'FAILED', data)

