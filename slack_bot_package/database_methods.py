from .database import *
from .database_models import BlacklistCategory, DoneParseApp, FavoritesDeveloper, TrashEmail




# db.query(Svazi).filter_by().all()
# db.add(new_svaz)
# db.commit()

def add_favorite_developer(developer_href):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    if db.query(FavoritesDeveloper).filter_by(dev_href=developer_href).first() == None:
        new_favorite = FavoritesDeveloper(dev_href=developer_href)
        db.add(new_favorite)
        db.commit()
        db.close()
    else:
        print('Уже есть в избранном')

def delete_favorite_developer(developer_href):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    if db.query(FavoritesDeveloper).filter_by(dev_href=developer_href).first() == None:
        print('Этого разработчика нет в избранном')
    else:
        del_favorite = db.query(FavoritesDeveloper).filter_by(dev_href=developer_href).first()
        db.delete(del_favorite)
        db.commit()
        db.close()


def get_blacklist_category():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    blacklist = []
    for a in db.query(BlacklistCategory).filter_by().all():
        blacklist.append(a.category_name)
    db.close()

    return blacklist


def add_done_parse_app(app_href, emails):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    new_done_parse_app = DoneParseApp(app_href=app_href, emails=", ".join(emails))
    db.add(new_done_parse_app)
    db.commit()
    db.close()

def get_list_done_parse_app():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    done_parse_list = []
    for a in db.query(DoneParseApp).filter_by().all():
        done_parse_list.append(a.app_href)
    db.close()

    return done_parse_list

def get_favorite_developer():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    favorite = []
    for a in db.query(FavoritesDeveloper).filter_by().all():
        favorite.append(a.dev_href)
    db.close()

    return favorite

def save_all_emails_apphref(app_href, list_emails):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    list_emails = ", ".join(list_emails)
    print(list_emails)
    new_trash = TrashEmail(app_href=app_href, trash_emails=list_emails)
    db.add(new_trash)
    db.commit()
    db.close()

def get_all_emails_apphref(app_href):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    emails = db.query(TrashEmail).filter_by(app_href=app_href).first().trash_emails
    db.close()

    return emails

def get_standart_email_apphref(app_href):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    emails = db.query(DoneParseApp).filter_by(app_href=app_href).first().emails
    db.close()

    return emails

def check_favorite(developer_href):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    if db.query(FavoritesDeveloper).filter_by(dev_href=developer_href).first() != None:
        db.close()
        return True
    else:
        db.close()
        return False