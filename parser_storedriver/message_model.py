class Message():
    def __init__(self, name_app, date_release, name_developer, count_app_in_acc,
                 type_app, category_app, all_mail_developer, href_app,
                 href_developer, count_emails, image_url_app, price_app=None, favorites=False):
        self.image_url_app = image_url_app
        self.count_emails = int(count_emails) - len(all_mail_developer)
        self.name_app = name_app
        self.date_release = date_release
        self.name_developer = name_developer
        self.count_app_in_acc = count_app_in_acc
        if self.count_app_in_acc == None:
            self.count_app_in_acc = 0
        self.type_app = type_app  # платное/бесплатное
        self.price_app = price_app
        if price_app == None:
            self.type_and_price = self.type_app
        else:
            self.type_and_price = "%s, %s" % (self.type_app, self.price_app)
        self.category_app = category_app
        self.all_mail_developer = ", ".join(all_mail_developer)
        self.href_app = href_app
        self.href_developer = href_developer
        self.favorites = favorites
        if self.favorites == True:
            self.add_prefix_app = ':star: '
        else:
            self.add_prefix_app = ''

    def create_slack_message(self):
        if self.favorites == True:
            self.slack_message = [
                {
                    "type": "divider"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "%s<%s|%s>" % (self.add_prefix_app, self.href_app, self.name_app)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📅 Дата релиза: %s\n"
                                "👤 Разработчик: <%s|%s>\n"
                                "🎮 Игр на аккаунте: %s\n"
                                "💵 Тип: %s\n"
                                "🧩Категория: %s\n"
                                "✉ email: %s\n" %
                                (self.date_release,
                                 self.href_developer, self.name_developer,
                                 self.count_app_in_acc,
                                 self.type_and_price,
                                 self.category_app,
                                 self.all_mail_developer)
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": self.image_url_app,
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📨 Показать все почты (%s)" % self.count_emails
                            },
                            "value": "all_emails"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⭐ Не паблишер"
                            },
                            "value": "add"
                        }
                    ]
                }
            ]
        else:
            self.slack_message = [
                {
                    "type": "divider"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "%s<%s|%s>" % (self.add_prefix_app, self.href_app, self.name_app)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📅 Дата релиза: %s\n"
                                "👤 Разработчик: <%s|%s>\n"
                                "🎮 Игр на аккаунте: %s\n"
                                "💵 Тип: %s\n"
                                "🧩Категория: %s\n"
                                "✉ email: %s\n" %
                                (self.date_release,
                                 self.href_developer, self.name_developer,
                                 self.count_app_in_acc,
                                 self.type_and_price,
                                 self.category_app,
                                 self.all_mail_developer)
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": self.image_url_app,
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📨 Показать все почты (%s)" % self.count_emails
                            },
                            "value": "all_emails"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⭐ Паблишер"
                            },
                            "value": "delete"
                        }
                    ]
                }
            ]

        return self.slack_message

def create_slack_message_for_update(app_href_name, text, trash, favorite, image_url_app, count_emails=''):
    if trash == True:
        if favorite == True:
            slack_message = [
                {
                    "type": "divider"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ':star: ' + app_href_name
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": image_url_app,
                        "alt_text": "cute cat"
                    }

                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📨 Скрыть все почты"
                            },
                            "value": "hide_all_emails"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⭐ Не паблишер"
                            },
                            "value": "delete"
                        }
                    ]
                }
            ]
        else:
            slack_message = [
                {
                    "type": "divider"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": app_href_name.replace(':star: ', '')
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": image_url_app,
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📨 Скрыть все почты"
                            },
                            "value": "hide_all_emails"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⭐ Паблишер"
                            },
                            "value": "add"
                        }
                    ]
                }
            ]
    elif trash == False:
        if favorite == True:
            slack_message = [
            {
                "type": "divider"
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ':star: ' + app_href_name
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {
                    "type": "image",
                    "image_url": image_url_app,
                    "alt_text": "cute cat"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📨 Показать все почты (%s)" % count_emails
                        },
                        "value": "all_emails"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "⭐ Не паблишер"
                        },
                        "value": "delete"
                    }
                ]
            }
        ]
        else:
            slack_message = [
                {
                    "type": "divider"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": app_href_name.replace(':star: ', '')
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": image_url_app,
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📨 Показать все почты (%s)" % count_emails
                            },
                            "value": "all_emails"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⭐ Паблишер"
                            },
                            "value": "add"
                        }
                    ]
                }
            ]

    return slack_message