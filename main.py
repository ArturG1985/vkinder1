from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from interface import BotInterface

from config import comunity_token, acces_token, \
    db_url_object

def main():

    engine = create_engine(db_url_object, echo=True)
    base = declarative_base()
    base.metadata.create_all(engine)
    bot = BotInterface(comunity_token, acces_token, engine=engine)
    bot.event_handler()


if __name__ == '__main__':
    main()
