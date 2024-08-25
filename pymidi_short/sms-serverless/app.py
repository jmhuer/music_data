import json
import urllib.parse
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from datetime import date
import boto3
from botocore.exceptions import ClientError
import threading


# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "chatgpt"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    # Your code goes here.
    secret_dict = json.loads(get_secret_value_response['SecretString'])

    secret = secret_dict['OPENAI_API_KEY']

    return secret


class AskGPTTimeout(Exception):
    pass

class AskGPTThread(threading.Thread):
    def __init__(self, messages):
        threading.Thread.__init__(self)
        self.messages = messages
        self.chat_completion = None

    def run(self):
        self.chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301", messages=self.messages
        )

def ask_gpt(messages):
    ask_gpt_thread = AskGPTThread(messages)
    ask_gpt_thread.start()

    ask_gpt_thread.join(timeout=52)  # Set the timeout to 15 seconds

    if ask_gpt_thread.is_alive():
        return "open ai api took too long!"
    
    reply = ask_gpt_thread.chat_completion.choices[0].message.content
    return reply


def get_history_from_s3(bucket, file_name):
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket, Key=file_name)
        s3.download_file(bucket, file_name, '/tmp/chat_history.txt')
        with open('/tmp/chat_history.txt', 'r') as f:
            messages = json.load(f)
        return messages
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Initialize a new conversation if the file doesn't exist
            messages = [{"role": "system", "content": "You are a helpful assistant. The following text comes from a text msg please respond well formatted for text. "}]
            return messages
        else:
            raise

def save_history_to_s3(bucket, file_name, messages):
    s3 = boto3.client('s3')
    with open('/tmp/chat_history.txt', 'w') as f:
        json.dump(messages, f)
    s3.upload_file('/tmp/chat_history.txt', bucket, file_name)

def lambda_handler(event, context):
    body = urllib.parse.parse_qs(event['body'])
    incoming_msg = body['Body'][0]
    openai.api_key  = get_secret()

    file_name = date.today().strftime("chat-history/%d-%m-%Y.txt")
    messages = get_history_from_s3('chatgpt-tools', file_name)

    messages.append({"role": "user", "content": incoming_msg},)
    reply = ask_gpt(messages)
    print(f"reply: {reply}")
    messages.append({"role": "assistant", "content": reply})

    save_history_to_s3('chatgpt-tools', file_name, messages)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply)

    return {
        'statusCode': 200,
        'body': str(resp),
        'headers': {
            'Content-Type': 'text/xml',
        }
    }