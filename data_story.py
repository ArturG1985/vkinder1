# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object

metadata = MetaData()
Base = declarative_base()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, primary_key=True)

class BdTools:
    def __init__(self, engine):
        self.engine = engine

    def add_user(self, profile_id, user_id):
        with Session(self.engine) as session:
            to_bd = Viewed(profile_id=profile_id, user_id=user_id)
            session.add(to_bd)
            session.commit()

    def check_user(self, profile_id, user_id):
        with Session(self.engine) as session:
            from_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id, Viewed.user_id == user_id).first()
            return True if from_bd else False


if __name__ == '__main__':

    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    #BdTools.add_user(engine, 12313321, 121321132)
    #res = BdTools.check_user(engine, 12313312, 121132132)
    #print(res)
   
