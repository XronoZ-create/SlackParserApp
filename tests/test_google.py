from parser_storedriver.google_play_scraper_master.google_play_scraper.scraper import PlayStoreScraper

develop = 'https://play.google.com/store/apps/dev?id=5843604371215345798'
store = PlayStoreScraper()

app_details = store.get_app_details(app_id='com.videomaker.videoeditor.PhotoVideoMaker.slideshow.softkeys')

print(app_details)