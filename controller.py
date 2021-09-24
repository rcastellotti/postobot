import logging
from os import getenv
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc
from datetime import datetime, timedelta

from models import Lecture

load_dotenv()

engine = create_engine(getenv("DATABASE_URL"), hide_parameters=True)


def insert_lecture(lectures):
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    session.merge(lectures)
    session.commit()
    session.close()
  except Exception as e:
    logging.exception(e)


def get_reservable_seats():
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    reservable_seats = session.query(Lecture).filter_by(qr="").order_by(asc(Lecture.lecture_timestamp)).all()
    session.close()
    return reservable_seats
  except Exception as e:
    logging.exception(e)


def get_reserved_seats():
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    reservable_seats = session.query(Lecture).filter(Lecture.qr != "").order_by(asc(Lecture.lecture_timestamp)).all()
    session.close()
    return reservable_seats
  except Exception as e:
      logging.exception(e)


def exists(entry_id, qr):
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    lecture = session.query(Lecture).filter_by(entry_id=entry_id).all()
    session.close()
    if qr:
      return len(lecture) > 0 and qr != ""
    return len(lecture) > 0
  except Exception as e:
    logging.exception(e)


def get_lecture(entry_id):
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    lecture = session.query(Lecture).filter_by(entry_id=entry_id).all()
    session.close()
    return lecture[0]
  except Exception as e:
    logging.exception(e)


def cleanup():
  try:
    Session = sessionmaker(bind=engine)
    session = Session()
    limit = datetime.now() - timedelta(hours=4)
    session.query(Lecture).filter(Lecture.lecture_timestamp < limit).delete()
    session.commit()
    session.close()
  except Exception as e:
    logging.exception(e)
