# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object

# схема БД
metadata = MetaData()
Base = declarative_base()


# пользоватль бота
class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.Text, nullable=True)
    bdate = sq.Column(sq.Text, nullable=True)
    home_town = sq.Column(sq.Text, nullable=True)
    shown = sq.Column(sq.Boolean, default=False)

# добавление записи в бд

def add_user(session, profile_id, user_id, name, bdate, home_town):
    to_bd = Viewed(
        profile_id=profile_id,
        user_id=user_id,
        name=name,
        bdate=bdate,
        home_town=home_town)
    session.add(to_bd)


# извлечение записей из БД
def check_user(session, profile_id, user_id):
    from_bd = session.query(Viewed).filter(
        Viewed.profile_id == profile_id,
        Viewed.user_id == user_id).first()
    return True if from_bd else False


def update_user_as_shown(session, profile_id, user_id):
    session.query(Viewed).filter(
        Viewed.profile_id == profile_id,
        Viewed.user_id == user_id).update({'shown': True})


def get_not_shown_users(session, user_id):
        from_bd = session.query(Viewed).filter(
            Viewed.user_id == user_id, not Viewed.shown).first()
        return from_bd


def number_of_not_shown_users(session, user_id):
    return session.query(Viewed).filter(
        Viewed.user_id == user_id, not Viewed.shown).count()


if __name__ == '__main__':

    engine = create_engine(db_url_object, echo=True)
    Base.metadata.create_all(engine)
    
