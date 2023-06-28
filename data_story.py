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


# добавление записи в бд

def add_user(engine, profile_id, user_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, user_id=user_id)
        session.add(to_bd)
        session.commit()

# извлечение записей из БД
def check_user(engine, profile_id, user_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id, Viewed.user_id == user_id).first()
        return True if from_bd else False


if __name__ == '__main__':

    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    add_user(engine, 12313, 121321)
    print(check_user(engine, 12313, 121321))