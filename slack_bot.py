# -*- coding: UTF-8 -*-

from slack_sdk.webhook import WebhookClient
import os
import json
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request, make_response
from parser_storedriver.message_model import create_slack_message_for_update
from slack_bot_package.database_methods import get_all_emails_apphref, get_standart_email_apphref,\
    add_favorite_developer, delete_favorite_developer, check_favorite
from slack_bot_package.slack_methods import update_message
from config import Config

signature_verifier = SignatureVerifier(
    signing_secret=Config.signing_secret
)

app = Flask(__name__)

@app.route("/slack", methods=["POST"])
def slack_app():
    print('gg')

    if not signature_verifier.is_valid(
            body=request.get_data(),
            timestamp=request.headers.get("X-Slack-Request-Timestamp"),
            signature=request.headers.get("X-Slack-Signature")):
        return make_response("invalid request", 403)

    payload_dict = json.loads(request.form.to_dict()['payload'])
    action = payload_dict['actions'][0]['value']
    print(payload_dict)
    print(action)
    print(payload_dict['container']['message_ts'])
    if action == 'add':
        developer_href = payload_dict['message']['blocks'][3]['text']['text'].split('\n')[1].split('👤 Разработчик: ')[0].replace('<', '').split('|')[0]
        add_favorite_developer(developer_href=developer_href)
        print(developer_href)

        ts = payload_dict['container']['message_ts']
        app_href_name = payload_dict['message']['blocks'][2]['text']['text']
        text = payload_dict['message']['blocks'][3]['text']['text']
        try:
            image_url_app = payload_dict['message']['blocks'][3]['accessory']['image_url']
        except:
            image_url_app = ''
        try:
            favorite = check_favorite(developer_href=developer_href)
            print(favorite)
            message_block = create_slack_message_for_update(app_href_name=app_href_name, text=text, trash=True,
                                                            favorite=favorite, image_url_app=image_url_app)
            update_message(ts=ts, block=message_block)
        except Exception as err:
            print(err)
    elif action == 'delete':
        developer_href = payload_dict['message']['blocks'][3]['text']['text'].split('\n')[1].split('👤 Разработчик: ')[0].replace('<', '').split('|')[0]
        delete_favorite_developer(developer_href=developer_href)
        print(developer_href)

        ts = payload_dict['container']['message_ts']
        app_href_name = payload_dict['message']['blocks'][2]['text']['text']
        text = payload_dict['message']['blocks'][3]['text']['text']
        try:
            image_url_app = payload_dict['message']['blocks'][3]['accessory']['image_url']
        except:
            image_url_app = ''
        try:
            favorite = check_favorite(developer_href=developer_href)
            message_block = create_slack_message_for_update(app_href_name=app_href_name, text=text, trash=True,
                                                            favorite=favorite, image_url_app=image_url_app)
            update_message(ts=ts, block=message_block)
        except Exception as err:
            print(err)
    elif action == 'all_emails':
        developer_href = payload_dict['message']['blocks'][3]['text']['text'].split('\n')[1].split('👤 Разработчик: ')[0].replace('<', '').split('|')[0]
        ts = payload_dict['container']['message_ts']
        app_href_name = payload_dict['message']['blocks'][2]['text']['text']
        text = payload_dict['message']['blocks'][3]['text']['text']
        try:
            image_url_app = payload_dict['message']['blocks'][3]['accessory']['image_url']
        except:
            image_url_app = ''
        try:
            all_emails = get_all_emails_apphref(app_href=app_href_name.replace('<', '').split('|')[0])
            text = text.split(':email: email: ')[0] + '✉ email: ' + all_emails
            print(text)
            favorite = check_favorite(developer_href=developer_href)
            message_block = create_slack_message_for_update(app_href_name=app_href_name, text=text, trash=True,
                                                            favorite=favorite, image_url_app=image_url_app)
            update_message(ts=ts, block=message_block)
        except Exception as err:
            print(err)
    elif action == 'hide_all_emails':
        developer_href = payload_dict['message']['blocks'][3]['text']['text'].split('\n')[1].split(':bust_in_silhouette: Разработчик: ')[0].replace('<', '').split('|')[0]
        ts = payload_dict['container']['message_ts']
        app_href_name = payload_dict['message']['blocks'][2]['text']['text']
        text = payload_dict['message']['blocks'][3]['text']['text']
        try:
            image_url_app = payload_dict['message']['blocks'][3]['accessory']['image_url']
        except:
            image_url_app = ''
        try:
            favorite = check_favorite(developer_href=developer_href)
            all_emails = get_standart_email_apphref(app_href=app_href_name.replace('<', '').split('|')[0])
            bd_emails = get_all_emails_apphref(app_href=app_href_name.replace('<', '').split('|')[0])
            if bd_emails == '':
                count_emails = 0
            else:
                count_emails = len(bd_emails.split(',')) - len(all_emails.split(','))
            text = text.split(':email: email: ')[0] + '✉ email: ' + all_emails
            message_block = create_slack_message_for_update(app_href_name=app_href_name, text=text, trash=False,
                                                            count_emails=count_emails, favorite=favorite,
                                                            image_url_app=image_url_app)
            update_message(ts=ts, block=message_block)
        except Exception as err:
            pass
    elif action == 'send_tmp_email':
        pass

    return make_response("", 200)

if __name__ == "__main__":
    app.run(debug=True)
