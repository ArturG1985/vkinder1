from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from interface import BotInterface
from bd import init_db
from config import comunity_token, acces_token, \
    db_url_object, db_username, db_password

def main():

    init_db(user=db_username, password=db_password)

    engine = create_engine(db_url_object)
    base = declarative_base()
    base.metadata.create_all(engine)
    bot = BotInterface(comunity_token, acces_token, engine=engine)
    bot.event_handler()


if __name__ == '__main__':
    main()
