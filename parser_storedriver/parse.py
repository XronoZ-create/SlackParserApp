from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from validate_email import validate_email
from parser_storedriver.google_play_scraper_master.google_play_scraper.scraper import PlayStoreScraper
from slack_bot_package.database_methods import save_all_emails_apphref, get_blacklist_category, get_list_done_parse_app, add_done_parse_app, get_favorite_developer
from parser_storedriver.message_model import Message
from slack_bot_package.slack_methods import send_slack_message
import traceback
from urllib.parse import urljoin
from textblob import TextBlob

def find_mail_in_html(page_source):
    print('Поиск почты на странице сайта')
    mail_developer = []
    bs = BeautifulSoup(page_source, "html.parser")

    for teg in ['span', 'a', 'p']:
        for html_elem in bs.find_all(teg):
            try:
                if html_elem['href'].find('@') != -1:
                    mail = html_elem['href'].replace('mailto:', '')
                    mail_developer.append(mail)
                    continue
            except Exception as err:
                pass
            try:
                if html_elem.get_text().find('@') != -1:
                    split_html_elem_text = html_elem.get_text().replace("\n", ' ')
                    mail = re.findall(r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+\w+[.A-Za-z0-9_]*', split_html_elem_text)[0]
                    mail_developer.append(mail)
            except Exception as err:
                pass
    return mail_developer

def redact_list_mails(list_mail, domain_site):
    print('Редактирование списка почт')
    print(domain_site)
    list_trash_emails = []
    list_valid_email = ['gmail.com', 'yahoo.com', 'hotmail.com', 'aol.com', 'hotmail.co.uk', 'hotmail.fr', 'msn.com', 'yahoo.fr', 'wanadoo.fr', 'orange.fr', 'comcast.net', 'yahoo.co.uk', 'yahoo.com.br', 'yahoo.co.in', 'live.com', 'rediffmail.com', 'free.fr', 'gmx.de', 'web.de', 'yandex.ru', 'ymail.com', 'libero.it', 'outlook.com', 'uol.com.br', 'bol.com.br', 'mail.ru', 'cox.net', 'hotmail.it', 'sbcglobal.net', 'sfr.fr', 'live.fr', 'verizon.net', 'live.co.uk', 'googlemail.com', 'yahoo.es', 'ig.com.br', 'live.nl', 'bigpond.com', 'terra.com.br', 'yahoo.it', 'neuf.fr', 'yahoo.de', 'alice.it', 'rocketmail.com', 'att.net', 'laposte.net', 'facebook.com', 'bellsouth.net', 'yahoo.in', 'hotmail.es', 'charter.net', 'yahoo.ca', 'yahoo.com.au', 'rambler.ru', 'hotmail.de', 'tiscali.it', 'shaw.ca', 'yahoo.co.jp', 'sky.com', 'earthlink.net', 'optonline.net', 'freenet.de', 't-online.de', 'aliceadsl.fr', 'virgilio.it', 'home.nl', 'qq.com', 'telenet.be', 'me.com', 'yahoo.com.ar', 'tiscali.co.uk', 'yahoo.com.mx', 'voila.fr', 'gmx.net', 'mail.com', 'planet.nl', 'tin.it', 'live.it', 'ntlworld.com', 'arcor.de', 'yahoo.co.id', 'frontiernet.net', 'hetnet.nl', 'live.com.au', 'yahoo.com.sg', 'zonnet.nl', 'club-internet.fr', 'juno.com', 'optusnet.com.au', 'blueyonder.co.uk', 'bluewin.ch', 'skynet.be', 'sympatico.ca', 'windstream.net', 'mac.com', 'centurytel.net', 'chello.nl', 'live.ca', 'aim.com', 'bigpond.net.au']
    redact_list = list(dict.fromkeys(list_mail[0]))
    redact_list_new = []
    for check_valid_mail in redact_list:
        try:
            if check_valid_mail[-1] == '.':
                b = list(check_valid_mail)
                b[-1] = ''
                check_valid_mail = ''.join(b)
            check_valid_mail = check_valid_mail.split('?')[0]
            if check_valid_mail.find("/@") != -1:
                continue

            if check_valid_mail.split('@')[1].split('.')[0] != domain_site.replace('www.', '').split('.')[0]:
                if check_valid_mail.find('https') != -1 \
                        or check_valid_mail.split('@')[1] not in list_valid_email:
                    print('Удаляем: ', check_valid_mail)
                    list_trash_emails.append(check_valid_mail)
                    continue
                else:
                    redact_list_new.append(check_valid_mail)
                    list_trash_emails.append(check_valid_mail)
            else:
                redact_list_new.append(check_valid_mail)
                list_trash_emails.append(check_valid_mail)
        except Exception as err:
            print(err)

    redact_list_new = list(dict.fromkeys(redact_list_new))
    list_trash_emails = list(dict.fromkeys(list_trash_emails))

    return [redact_list_new, list_trash_emails]

def check_category_blacklist(category_app, blacklist):
    for a in blacklist:
        for b in category_app.split(' |'):
            if a == b:
                return True
    return False

class ParseStoreDriver():
    def __init__(self):
        self.prefs = {
            "download_restrictions": 3,
        }

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('ignore-certificate-errors')
        self.options.add_argument('--no-sandbox')

        self.options.add_argument("enable-automation")
        self.options.add_argument("--headless")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--dns-prefetch-disable")
        self.options.add_argument("--disable-gpu")
        self.options.add_experimental_option(
            "prefs", self.prefs
        )

        self.client = webdriver.Chrome(chrome_options=self.options)
        self.client.set_page_load_timeout(10)
        self.blacklist = get_blacklist_category()

    def find_info_developer_ios(self, href_developer, href_app):
        print('Поиск инфы ios приложения')
        try:
            self.split_url = href_developer.split('/')
            self.split_url[3] = 'us'
            self.redact_url = '/'.join(self.split_url)
            self.client.get(self.redact_url)
            self.bs = BeautifulSoup(self.client.page_source, "html.parser")
            if self.bs.find('section', {'class':'l-content-width section section--bordered'}).find('a', string='See All').get('style') == None:
                self.client.find_element_by_xpath("//*[contains(text(), 'See All')]").click()
                time.sleep(2)
                self.bs = BeautifulSoup(self.client.page_source, "html.parser")
                self.count_app = len(self.bs.find('div', {'class': 'l-row'}).find_all('a', recursive=False))
            else:
                self.count_app = len(self.bs.find('div', {'class':'l-row l-row--peek'}).find_all('a', recursive=False))
        except Exception:
            self.count_app = None

        for a in range(1,5):
            try:
                self.client.get(href_app)
                self.bs = BeautifulSoup(self.client.page_source, "html.parser")

                #  Проверка условий для публикации сообшения в Slack-чат
                if TextBlob(self.bs.find('div', {'class': 'section__description'}).find('p').get_text()).detect_language() != 'en':
                    print('Не английское описание: %s' % self.bs.find('div', {'class': 'section__description'}).find('p').get_text())
                    raise NonEnglishDescript  # Если не английское описание

                self.url_website = self.bs.find('ul', {'class': 'inline-list inline-list--app-extensions'}).find('li').find('a')['href']
                break
            except NonEnglishDescript:
                raise NonEnglishDescript
            except Exception as err:
                print(err)

        self.mail_developer = [[], []]

        try:
            self.client.get(self.url_website)
        except:
            try:
                self.client.execute_script("window.stop();")
            except Exception as err:
                print(err)
        time.sleep(1)
        self.mail_developer[0] = self.mail_developer[0] + find_mail_in_html(self.client.page_source)

        self.bs = BeautifulSoup(self.client.page_source, "html.parser")
        self.all_hrefs_in_site = self.bs.find_all(href=True)
        self.hrefs_site = []
        for self.href_one in self.all_hrefs_in_site:
            if self.href_one['href'] == '/' or \
                    self.href_one['href'].find('.png') != -1 or \
                    self.href_one['href'].find('.jpg') != -1 or\
                    self.href_one['href'].find('.css') != -1 or \
                    self.href_one['href'].find('.js') != -1 or \
                    self.href_one['href'].find('.svg') != -1 or \
                    self.href_one['href'].find('.ico') != -1 or \
                    self.href_one['href'].find('.pdf') != -1 or \
                    self.href_one['href'].find('instagram') != -1 or \
                    self.href_one['href'].find('facebook') != -1 or \
                    self.href_one['href'].find('vk.com') != -1 or \
                    self.href_one['href'].find('.xml') != -1 or \
                    self.href_one['href'].find('.woff2') != -1 or \
                    self.href_one['href'].find('.zip') != -1 or \
                    self.href_one['href'].find('.pptx') != -1 or \
                    self.href_one['href'].find('.woff') != -1 or \
                    self.href_one['href'].find('.exe') != -1 or \
                    self.href_one['href'].find('.apk') != -1:
                continue
            else:
                self.hrefs_site.append(urljoin(self.url_website, self.href_one['href']))
        self.hrefs_site = list(dict.fromkeys(self.hrefs_site))

        for self.url_page in self.hrefs_site:
            try:
                self.client.get(self.url_page)
            except:
                try:
                    self.client.execute_script("window.stop();")
                except Exception as err:
                    print(err)
            time.sleep(1)
            try:
                self.mail_developer[0] = self.mail_developer[0] + find_mail_in_html(self.client.page_source)
            except Exception as err:
                print(err)

        print(self.mail_developer)
        self.mail_developer = redact_list_mails(list_mail=self.mail_developer, domain_site=self.url_website.split('//')[1].split('/')[0])
        return {'count_app': self.count_app, 'all_mail': self.mail_developer[0], 'all_emails_trash': self.mail_developer[1]}

    def find_info_developer_android(self, href_developer, href_app):
        print('Поиск инфы android приложения')
        self.store = PlayStoreScraper()
        self.develop = href_developer.replace('https://play.google.com/store/apps/developer?id=', '').replace('+', ' ').split('&')[0]
        self.develop = self.develop.replace('https://play.google.com/store/apps/dev?id=', '').replace('+', ' ').split('&')[0]
        try:
            self.app_ids = self.store.get_app_ids_for_developer(self.develop, country='us')
            self.count_app = len(self.app_ids)
        except:
            self.count_app = None

        self.mail_developer = [[], []]
        try:
            self.app_details = self.store.get_app_details(app_id=href_app.split("id=")[1])

            #  Проверка условий для публикации сообшения в Slack-чат
            if TextBlob(self.app_details['description']).detect_language() != 'en':
                print('Не английское описание: %s' % self.app_details['description'])
                raise NonEnglishDescript  # Если не английское описание

            self.url_website = self.app_details['site_developer']
            self.mail_developer[0].append(self.app_details['email_developer'])
        except NonEnglishDescript:
            raise NonEnglishDescript
        except Exception:
            self.url_website = None

        if self.url_website == None:
            return {'count_app': self.count_app, 'all_mail': self.mail_developer[0], 'all_emails_trash': self.mail_developer[0]}
        try:
            self.client.get(self.url_website)
            time.sleep(2)
        except:
            try:
                self.client.execute_script("window.stop();")
            except Exception as err:
                print(err)
        self.bs = BeautifulSoup(self.client.page_source, "html.parser")
        self.all_hrefs_in_site = self.bs.find_all(href=True)
        self.hrefs_site = []
        for self.href_one in self.all_hrefs_in_site:
            if self.href_one['href'] == '/' or \
                    self.href_one['href'].find('.png') != -1 or \
                    self.href_one['href'].find('.jpg') != -1 or \
                    self.href_one['href'].find('.css') != -1 or \
                    self.href_one['href'].find('.js') != -1 or \
                    self.href_one['href'].find('.svg') != -1 or \
                    self.href_one['href'].find('.ico') != -1 or \
                    self.href_one['href'].find('.pdf') != -1 or \
                    self.href_one['href'].find('instagram') != -1 or \
                    self.href_one['href'].find('facebook') != -1 or \
                    self.href_one['href'].find('vk.com') != -1 or \
                    self.href_one['href'].find('.xml') != -1 or \
                    self.href_one['href'].find('.woff2') != -1 or \
                    self.href_one['href'].find('.zip') != -1 or \
                    self.href_one['href'].find('.pptx') != -1 or \
                    self.href_one['href'].find('.woff') != -1 or \
                    self.href_one['href'].find('.exe') != -1 or \
                    self.href_one['href'].find('.apk') != -1:
                continue
            else:
                self.hrefs_site.append(urljoin(self.url_website, self.href_one['href']))
        self.hrefs_site = list(dict.fromkeys(self.hrefs_site))

        for self.url_page in self.hrefs_site:
            try:
                self.client.get(self.url_page)
                time.sleep(2)
            except:
                try:
                    self.client.execute_script("window.stop();")
                except Exception as err:
                    print(err)
            try:
                self.mail_developer[0] = self.mail_developer[0] + find_mail_in_html(self.client.page_source)
            except Exception as err:
                print(err)

        self.mail_developer = redact_list_mails(list_mail=self.mail_developer, domain_site=self.url_website.split('//')[1].split('/')[0])
        return {'count_app': self.count_app, 'all_mail': self.mail_developer[0], 'all_emails_trash': self.mail_developer[1]}


    def find_new_app_ios(self):
        self.page_num = 1
        self.list_done_parse = get_list_done_parse_app()

        for self.a in range(1, 3):
            self.url = 'https://app.storedrive.io/newapps/ios?appType=0&limit=150&orderBy=release&page=%s'
            self.client.get(self.url % self.page_num)
            time.sleep(3)
            self.bs_main = BeautifulSoup(self.client.page_source, "html.parser")
            self.new_app = self.bs_main.find('div', {'id': 'applications'}).find_all('div', recursive=False)

            for self.app in self.new_app:
                try:
                    self.image_url = self.app.find('div', {'class': 'app_image mr-3'}).find('img')['src']
                    self.date_release = self.app.find('div', {'class': 'app_dates'}).get_text().split('|')[0].split(': ')[1].replace('\n', '')
                    self.href_developer = self.app.find('div', {'class': 'app_info'}).find('a')['href']
                    self.app_categories = self.app.find('ul', {'class': 'app_categories'}).get_text().replace('\n', '')
                    self.href_app = self.app.find('a', {'class': 'app_name'})['href']
                    if self.date_release != datetime.now().strftime("%Y-%m-%d") or\
                            check_category_blacklist(category_app=self.app_categories, blacklist=self.blacklist) or \
                            self.href_app in self.list_done_parse:
                        continue
                    self.name_app = self.app.find('a', {'class': 'app_name'}).get_text().replace('\n', '')
                    self.name_developer = self.app.find('div', {'class': 'app_info'}).find('a').get_text().replace('\n', '')
                    self.count_app_in_acc = None
                    print(self.name_app)
                    try:
                        self.type_app = self.app.find('div', {'class': 'd-md-inline-block d-block'}).find('a').get_text().replace('\n', '')
                        self.price_app = self.app.find('div', {'class': 'd-md-inline-block d-block'}).find('a')['data-content']
                    except:
                        self.type_app = self.app.find('div', {'class': 'd-md-inline-block d-block'}).get_text().replace('\n', '').split('|')[1]
                        self.price_app = None
                    self.all_mail_developer = None

                    self.info_developer = self.find_info_developer_ios(self.href_developer, self.href_app)
                    save_all_emails_apphref(list_emails=self.info_developer['all_emails_trash'], app_href=self.href_app)

                    self.count_app_in_acc = self.info_developer['count_app']
                    self.all_mail_developer = self.info_developer['all_mail']

                    print(self.date_release, self.name_app, self.name_developer, self.type_app, self.price_app,self.app_categories, self.href_developer, self.href_app, self.count_app_in_acc, self.all_mail_developer)
                    if self.href_developer in get_favorite_developer():
                        self.favorite_dev = True
                    else:
                        self.favorite_dev = False

                    #  Проверка условий для публикации сообшения в Slack-чат
                    if len(self.info_developer['all_emails_trash']) == 0:
                        print('Ноль почт. Не отправляем сообщение')
                        continue  # Убрать из выборки те проекты у которых вообще нет почты

                    self.message_exemp = Message(name_app=self.name_app,
                                                 date_release=self.date_release,
                                                 name_developer=self.name_developer,
                                                 count_app_in_acc=self.count_app_in_acc,
                                                 type_app=self.type_app,
                                                 category_app=self.app_categories,
                                                 all_mail_developer=self.all_mail_developer,
                                                 href_app=self.href_app,
                                                 href_developer=self.href_developer,
                                                 price_app=self.price_app, favorites=self.favorite_dev,
                                                 count_emails=len(self.info_developer['all_emails_trash']),
                                                 image_url_app=self.image_url)
                    send_slack_message(self.message_exemp.create_slack_message())
                    add_done_parse_app(self.href_app, emails=self.all_mail_developer)
                except Exception:
                    traceback.print_exc()
                self.client.quit()
                self.client = webdriver.Chrome(chrome_options=self.options)
                self.client.set_page_load_timeout(10)
            self.page_num += 1
        self.client.quit()
        self.client = webdriver.Chrome(chrome_options=self.options)
        self.client.set_page_load_timeout(10)

    def find_new_app_android(self):
        self.page_num = 1
        self.list_done_parse = get_list_done_parse_app()

        for self.a in range(1, 3):
            self.url = 'https://app.storedrive.io/newapps/android?appType=0&limit=150&orderBy=release&page=%s'
            self.client.get(self.url % self.page_num)
            time.sleep(3)
            self.bs_main = BeautifulSoup(self.client.page_source, "html.parser")
            self.new_app = self.bs_main.find('div', {'id': 'applications'}).find_all('div', recursive=False)

            for self.app in self.new_app:
                try:
                    self.image_url = self.app.find('div', {'class': 'app_image mr-3'}).find('img')['src']
                    self.date_release = self.app.find('div', {'class': 'app_dates'}).get_text().split('|')[0].split(': ')[1].replace('\n', '')
                    self.href_developer = self.app.find('div', {'class': 'app_info'}).find('a')['href']
                    self.app_categories = self.app.find('ul', {'class': 'app_categories'}).get_text().replace('\n', '')
                    self.href_app = self.app.find('a', {'class': 'app_name'})['href']
                    if check_category_blacklist(category_app=self.app_categories, blacklist=self.blacklist) or \
                            self.href_app in self.list_done_parse:
                        continue
                    self.name_app = self.app.find('a', {'class': 'app_name'}).get_text().replace('\n', '')
                    self.name_developer = self.app.find('div', {'class': 'app_info'}).find('a').get_text().replace('\n', '')
                    self.count_app_in_acc = None
                    print(self.name_app)
                    try:
                        self.type_app = self.app.find('div', {'class': 'd-md-inline-block d-block'}).find(
                            'a').get_text().replace('\n', '')
                        self.price_app = self.app.find('div', {'class': 'd-md-inline-block d-block'}).find('a')[
                            'data-content']
                    except:
                        self.type_app = \
                        self.app.find('div', {'class': 'd-md-inline-block d-block'}).get_text().replace('\n', '').split(
                            '|')[1]
                        self.price_app = None
                    self.all_mail_developer = None

                    self.info_developer = self.find_info_developer_android(self.href_developer, self.href_app)
                    save_all_emails_apphref(list_emails=self.info_developer['all_emails_trash'], app_href=self.href_app)

                    self.count_app_in_acc = self.info_developer['count_app']
                    self.all_mail_developer = self.info_developer['all_mail']

                    print(self.date_release, self.name_app, self.name_developer, self.type_app, self.price_app,self.app_categories, self.href_developer, self.href_app, self.count_app_in_acc, self.all_mail_developer)
                    if self.href_developer in get_favorite_developer():
                        self.favorite_dev = True
                    else:
                        self.favorite_dev = False

                    #  Проверка условий для публикации сообшения в Slack-чат
                    if len(self.info_developer['all_emails_trash']) == 0:
                        print('Ноль почт. Не отправляем сообщение')
                        continue  # Убрать из выборки те проекты у которых вообще нет почты

                    self.message_exemp = Message(name_app=self.name_app,
                                                 date_release=self.date_release,
                                                 name_developer=self.name_developer,
                                                 count_app_in_acc=self.count_app_in_acc,
                                                 type_app=self.type_app,
                                                 category_app=self.app_categories,
                                                 all_mail_developer=self.all_mail_developer,
                                                 href_app=self.href_app,
                                                 href_developer=self.href_developer,
                                                 price_app=self.price_app,
                                                 favorites=self.favorite_dev,
                                                 count_emails=len(self.info_developer['all_emails_trash']),
                                                 image_url_app=self.image_url)
                    send_slack_message(self.message_exemp.create_slack_message())
                    add_done_parse_app(self.href_app, emails=self.all_mail_developer)
                except Exception:
                    traceback.print_exc()
                self.client.quit()
                self.client = webdriver.Chrome(chrome_options=self.options)
                self.client.set_page_load_timeout(10)
            self.page_num += 1
        self.client.quit()
        self.client = webdriver.Chrome(chrome_options=self.options)
        self.client.set_page_load_timeout(10)


class NonEnglishDescript(Exception):
    pass