from celery import Celery
from parser_storedriver.parse import ParseStoreDriver
import time

celery = Celery('parse_storedriver', broker='amqp://')
celery.conf.beat_schedule = {
    'add-every-5h-option': {
        'task': 'parse_queued.start_parse',
        'schedule': 18000,
    },
}
celery.conf.timezone = 'UTC'
@celery.task()
def start_parse():
    parse = ParseStoreDriver()
    try:
        print('ПАРСИМ ИГРЫ IOS')
        parse.find_new_app_ios()
        print('ПАРСИМ ИГРЫ ANDROID')
        parse.find_new_app_android()
        parse.client.quit()
    except Exception as err:
        print(err)
