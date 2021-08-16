from parser_storedriver.message_model import Message
from slack_bot_package.slack_methods import send_slack_message

message_exemp = Message(
    name_app='name_app',
     date_release='date_release',
     name_developer='name_developer',
     count_app_in_acc='count_app_in_acc',
     type_app='type_app',
     category_app='app_categories',
     all_mail_developer='all_mail_developer',
     href_app='href_app',
     href_developer='href_developer',
     price_app='price_app'
)
send_slack_message(message_exemp.create_slack_message())