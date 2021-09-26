from models import Lecture
from dotenv import load_dotenv
from os import getenv
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from utils import delete_booking
import asyncio

load_dotenv()
engine = create_engine(getenv("DATABASE_URL"), hide_parameters=True)


async def sprenota():
    Session = sessionmaker(bind=engine)
    session = Session()
    reservable_seats = session.query(Lecture.entry_id).all()
    for item in reservable_seats:
        await delete_booking(item[0], "4801634")


if __name__ == "__main__":
    asyncio.run(sprenota())
