import urllib3
import urllib.parse
import openai
import os
import re
import json
import base64
import requests
from io import BytesIO
from PIL import Image

http = urllib3.PoolManager()
openai.api_key = os.environ["API_KEY"]

def image(prompt):
    response = openai.Image.create(
        model="image-alpha-001",
        prompt=prompt,
        size="256x256"
    )

    image_url = response["data"][0]["url"]
    image_data = requests.get(image_url).content
    img = Image.open(BytesIO(image_data))

    return img

def extract_input(lookup_key, decoded_string):
    pattern = re.compile(fr"{lookup_key}=([^&]+)")
    match = pattern.search(decoded_string)
    if match:
        input_text = match.group(1)
        input_text = urllib.parse.unquote_plus(input_text)
        return input_text
    else:
        return None
  
def lambda_handler(event, context):
    print("Event: ")
    print(event)
    decoded_string = base64.b64decode(event["body"]).decode("utf-8") #input from slack
    print("Event body decoded: ")
    print(decoded_string)
    decoded_input = extract_input("text", decoded_string) #gets the return from the function
    channel_id = extract_input("channel_id", decoded_string)
    channel_name = extract_input("channel_name", decoded_string)
    print(f"Channel_ID: {channel_id}")
    print(f"Channel_Name: {channel_name}")
  
    print(decoded_input)
    img = image(decoded_input) #holds the return from the image generation service
  
    SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
    Post_Message = os.environ["Post_Message"]
    OAuth = os.environ['OAuth_Token']
  
    payload = {
        "channel": channel_id,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Question:* {decoded_input}"
                }
            },
            {
                "type": "image",
                "image_url": img,
                "alt_text": "Generated Image"
            }
        ]
    }
  
    print(payload)
    encoded_data = json.dumps(payload).encode('utf-8')
    response =  http.request(
                'POST',
                Post_Message,
                body=encoded_data,
                headers={'Content-Type': 'application/json',
                'Authorization': f'Bearer {OAuth}'})
                
    print(response.status)
    print(response.data)
