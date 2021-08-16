from selenium import webdriver
from parser_storedriver.parse import find_mail_in_html
from bs4 import BeautifulSoup

client = webdriver.Chrome()
client.get('https://email-verify.my-addr.com/list-of-most-popular-email-domains.php')

c = []
a = BeautifulSoup(client.page_source).find('div', {'class': 'middle_info_noborder'}).find_all('tr')
for b in a:
    c.append(b.find_all('td')[2].get_text())
print(c)