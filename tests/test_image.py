from parser_storedriver.message_model import Message
from slack_bot_package.slack_methods import send_slack_message

send_slack_message(
    Message(
        'name_app', 'date_release', 'name_developer', 'count_app_in_acc',
        'type_app', 'category_app', 'all_mail_developer', 'href_app',
        'href_developer', '10',
        'https://is2-ssl.mzstatic.com/image/thumb/Purple114/v4/b2/86/62/b28662e9-77fe-de60-6180-7d0b1d61c12e/AppIcon-1x_U007emarketing-0-5-0-85-220.png/100x100bb.jpg'
    ).create_slack_message()
)