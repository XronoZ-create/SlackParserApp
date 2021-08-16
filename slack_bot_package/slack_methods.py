from slack_sdk.webhook import WebhookClient
from slack_sdk.web import WebClient
from config import Config

url = Config.url
token = Config.token
channel = Config.channel

def send_slack_message(block):
    webhook = WebhookClient(url)
    client = WebClient(token=token)
    response = client.chat_postMessage(
        blocks=block, channel=channel)
    # print(response)


def update_message(ts, block):
    client = WebClient(token=token)
    a = client.chat_update(channel=channel, ts=ts, blocks=block)
    print(a)