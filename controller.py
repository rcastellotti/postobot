from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event, engine
import os
from dotenv import load_dotenv
from sqlalchemy import exc
import logging
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), hide_parameters=True)


def insert_lecture(lecture):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(lecture)
    try:
        session.commit()
    except exc.SQLAlchemyError as e:
        logging.exception("lezione gia' presente")
