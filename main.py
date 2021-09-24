from sqlalchemy.sql.expression import insert
from controller import get_reservable_seats, insert_lecture, get_reserved_seats
import os
import math
import numpy
import requests
import threading
import dateparser
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from sqlalchemy.exc import IntegrityError
from aiogram.utils import executor
import logging
import json
from db import Lecture
from bs4 import BeautifulSoup


WELCOME_STR = """
Questo bot permette di prenotare un posto a lezione per il corso di informatica del terzo anno di UniGe.\n
/disponibili mostra le lezioni che possono essere prenotate.
/prenota avvia la procedura di prenotazione.
/annulla annulla la procedura di prenotazione.
"""


EA_LOGIN_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=login&include=login&from=prenotalezione&from_include=prenotalezione_home&_lang=it"
BOOKING_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=prenotalezione&include=prenotalezione"
API_URL = "https://easyacademy.unige.it/portalestudenti/call_ajax.php"
PROFILE_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=prenotalezione&include=prenotalezione_profilo&_lang=it"

load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"))
dispatcher = Dispatcher(bot, storage=MemoryStorage())
lock = threading.Lock()
bookings = []


def wait_until_present(driver, xpath=None, class_name=None, el_id=None, name=None, duration=5, frequency=0.01):
    if xpath:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.XPATH, xpath)))
    elif class_name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.ID, el_id)))
    elif name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.NAME, name)))


def js_click(driver, element):
    driver.execute_script("arguments[0].click()", element)


def get_json(phpsessid, url, var_identifier):
    cookies = {"PHPSESSID": f"{phpsessid}"}
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    lessons = str(soup).split(var_identifier)[1].split("') ;")[0]
    return json.loads(lessons)


def parse_json(json):
    bookings = []
    for booking_group in json:
        qr = booking_group["qr"]
        sede = booking_group["sede"]
        ora_inizio = booking_group["ora_inizio"]
        ora_fine = booking_group["ora_fine"]
        # la vuole in formato Monday 27 September 2021
        data_lezione = booking_group["data"]
        for booking in booking_group["prenotazioni"]:
            ora_inizio_lezione = booking["ora_inizio"]
            ora_fine_lezione = booking["ora_fine"]
            aula = booking["aula"]
            entry_id = booking["entry_id"]
            nome = booking["nome"]
            lecture = Lecture(entry_id=entry_id, sede=sede, aula=aula, data_lezione=data_lezione, ora_inizio=ora_inizio,
                              ora_fine=ora_fine, qr=qr, nome=nome, ora_inizio_lezione=ora_inizio_lezione, ora_fine_lezione=ora_fine_lezione)
            bookings.append(lecture)
    return bookings


def ea_login(driver):
    driver.get(EA_LOGIN_URL)
    login_button = wait_until_present(driver, el_id="oauth_btn")
    switches = driver.find_elements_by_class_name("switch")
    for switch in switches:
        js_click(driver, switch)
    js_click(driver, login_button)
    return driver.get_cookies()[0]["value"]


def ug_login(driver, username, password):
    wait_until_present(driver, el_id="username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.execute_script("document.getElementsByName('f')[0].submit()")


def get_bookings(url, var_identifier):
    bookings = []
    options = webdriver.firefox.options.Options()
    options.headless = False
    driver = webdriver.Firefox(options=options)
    try:
        phpsessid = ea_login(driver)
        ug_login(driver, os.getenv("ID"), os.getenv("PASSWORD"))
        sleep(2)
        json = get_json(phpsessid, url, var_identifier)
        bookings = parse_json(json)
    except Exception as e:
        logging.exception(e)
    driver.quit()
    return bookings


def pippo():
    options = webdriver.firefox.options.Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    try:
        ea_login(driver)
        ug_login(driver, os.getenv("ID"), os.getenv("PASSWORD"))
        reservable_seats = get_bookings(
            BOOKING_URL, "var lezioni_prenotabili = JSON.parse('")
        [insert_lecture(lecture) for lecture in reservable_seats]
        reserved_seats = get_bookings(
            f"{BOOKING_URL}_gestisci", "var lezioni_prenotate = JSON.parse('")
        [insert_lecture(lecture) for lecture in reserved_seats]
    except Exception as e:
        logging.exception(e)
    driver.quit()


def update_available_bookings(thread=False):
    while True:
        pippo()
        sleep(60 * 60)


class BookingRequest(StatesGroup):
    label = State()
    username = State()


def parse_booking(label):
    data = label.split("\n")
    datetime = data[0].split(" ")
    date = datetime[0]
    time = datetime[1]
    subject = data[1]
    room = data[2]
    for booking in bookings:
        if booking.date == date and booking.time == time and booking.subject == subject and booking.room == room:
            return booking.id
    return None


async def get_labels(bookings):
    return [str(booking) for booking in bookings]


async def gen_markup(data, step):
    labels = await get_labels(data)
    pool = numpy.array_split(labels, math.ceil(len(labels) / step))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for elems in pool:
        markup.add(*elems)
    return markup


async def book(lesson_id, username):
    params = {
        "mode": "salva_prenotazioni",
        "codice_fiscale": username,
        "id_entries": f"[{lesson_id}]"
    }
    res = requests.get(API_URL, params=params)
    logging.info(res.text)
    if "presente" in res.text:
        return -1
    elif "Trying to get property 'ID' of non-object" in res.text:
        return -2
    return 0


@ dispatcher.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply(WELCOME_STR)


@ dispatcher.message_handler(commands="disponibili")
async def reservable_seats(message: types.Message):
    reservable_seats = get_reservable_seats()
    if len(reservable_seats) < 1:
        await message.reply("Non ci sono lezioni prenotabili.")
    else:
        await message.reply("\n\n".join(await get_labels(reservable_seats)))


@ dispatcher.message_handler(commands="prenotate")
async def reserved_seats(message: types.Message):
    reserved_seats = get_reserved_seats()
    if len(reserved_seats) < 1:
        await message.reply("Non ci sono lezioni prenotate.")
    else:
        await message.reply("\n\n".join(await get_labels(reserved_seats)))


@ dispatcher.message_handler(commands="prenota")
async def booking_request(message: types.Message):
    await BookingRequest.label.set()
    markup = await gen_markup(bookings, 1)
    await message.reply("Scegli la lezione.", reply_markup=markup)


@ dispatcher.message_handler(state="*", commands="annulla")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Annullato.", reply_markup=types.ReplyKeyboardRemove())


@ dispatcher.message_handler(lambda message: parse_booking(message.text) is None, state=BookingRequest.label)
async def process_invalid_label(message: types.Message):
    await message.reply("Scelta errata!\nRiprova.")


@ dispatcher.message_handler(state=BookingRequest.label)
async def process_label(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["label"] = message.text
    await BookingRequest.next()
    await message.reply("Inserisci la tua matricola (7 cifre).", reply_markup=types.ReplyKeyboardRemove())


@ dispatcher.message_handler(lambda message: len(message.text) != 7 or not message.text.isdigit(), state=BookingRequest.username)
async def process_invalid_username(message: types.Message):
    await message.reply("Matricola errata!\nRiprova.")


@ dispatcher.message_handler(state=BookingRequest.username)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        booking_id = parse_booking(data["label"])
        username = message.text
    result = await book(booking_id, username)
    if result == -1:
        await bot.send_message(message.chat.id, "Ti sei già prenotato per questa lezione.")
    elif result == -2:
        await bot.send_message(message.chat.id, f"La matricola non esiste oppure non hai ancora impostato un profilo, fallo [qui]({PROFILE_URL})", parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(message.chat.id, "Prenotazione effettuata, riceverai una mail con il QR code.")
    await state.finish()


if __name__ == "__main__":
    pippo()
    # threading.Thread(target=update_available_bookings).start()
    executor.start_polling(dispatcher)
