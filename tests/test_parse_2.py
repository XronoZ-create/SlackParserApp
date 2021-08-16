from parser_storedriver.parse import find_mail_in_html
from selenium import webdriver

url_site = 'http://shellinfra.com/'

client = webdriver.Chrome()
client.get(url_site)

a = find_mail_in_html(client.page_source)
print(a)