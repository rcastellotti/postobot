from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event, engine, asc
import os
from dotenv import load_dotenv
from sqlalchemy import exc
from models import Lecture
import logging
from datetime import datetime, timedelta
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), hide_parameters=True)
logger = logging.getLogger('sqlalchemy')
logger.propagate = False


def insert_lecture(lectures):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.merge(lectures)
    try:
        session.commit()
    except exc.SQLAlchemyError as e:
        logging.exception("lezione gia' presente")

# error handling try catch generici


def get_reservable_seats():
    Session = sessionmaker(bind=engine)
    session = Session()
    reservable_seats = session.query(Lecture).filter_by(
        qr="").order_by(asc(Lecture.lecture_timestamp)).all()
    return reservable_seats


def get_reserved_seats():
    Session = sessionmaker(bind=engine)
    session = Session()
    reservable_seats = session.query(Lecture).filter(
        Lecture.qr != "").order_by(asc(Lecture.lecture_timestamp)).all()
    return reservable_seats


def exists(entry_id, qr):
    Session = sessionmaker(bind=engine)
    session = Session()
    lecture = session.query(Lecture).filter_by(entry_id=entry_id).all()
    if qr:
        return len(lecture) > 0 and qr != ""
    return len(lecture) > 0


def get_lecture(entry_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    lecture = session.query(Lecture).filter_by(entry_id=entry_id).all()
    return lecture[0]


def cleanup():
    Session = sessionmaker(bind=engine)
    session = Session()
    limit = datetime.now() - timedelta(hours=8)
    session.query(Lecture).filter(Lecture.lecture_timestamp < limit).delete()
    session.commit()
