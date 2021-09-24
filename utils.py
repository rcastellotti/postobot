from controller import insert_lecture, exists, get_lecture, cleanup
import os
import math
import numpy
import requests
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot, types
from aiogram.types import InputFile
import logging
import json
from models import Lecture
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
from io import BytesIO

EA_LOGIN_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=login&include=login&from=prenotalezione&from_include=prenotalezione_home&_lang=it"
BOOKING_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=prenotalezione&include=prenotalezione"
API_URL = "https://easyacademy.unige.it/portalestudenti/call_ajax.php"

load_dotenv()
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
    options.headless = True
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


def get_qr_bytes(lecture):
    data = {
        "language": "en",
        "matricola": os.getenv("ID"),
        "color": "333333",
        "qr": lecture.qr,
        "sede": lecture.sede,
        "ora_inizio": lecture.ora_inizio,
        "ora_fine": lecture.ora_fine,
        "data_lezione": f"{datetime.strptime(lecture.data_lezione, '%d/%m/%Y').strftime('%A %d %B %Y')}",
        "ora_prima_lezione": lecture.ora_inizio,
        "prenotazioni[]": f"true|{lecture.nome}|{lecture.ora_inizio_lezione} - {lecture.ora_fine_lezione}|{lecture.aula}|0"
    }
    response = requests.post(
        "https://easyacademy.unige.it/portalestudenti/export_pdf2.php", data=data)
    return BytesIO(response.content)


def aux_update(entry_id, chat_id):
    asyncio.run(update_and_send_qr(entry_id, chat_id))


async def update_and_send_qr(entry_id, chat_id):
    pippo()
    lecture = get_lecture(entry_id)
    qr_bytes = get_qr_bytes(lecture)
    bot2 = Bot(os.getenv("BOT_TOKEN"))
    qr_file = InputFile(qr_bytes, f"qr_{lecture.entry_id}.pdf")
    await bot2.send_document(chat_id, qr_file)
    await bot2.close()


def db_cleanup():
    while True:
        cleanup()
        sleep(60 * 60)


def parse_booking(label, qr=False):
    data = label.split("\n")
    entry_id = data[0]
    if not entry_id.isnumeric() or len(entry_id) != 7:
        return None
    if exists(entry_id, qr):
        return entry_id
    return None


async def get_labels(bookings):
    return [str(booking) for booking in bookings]


async def gen_markup(data, step):
    labels = await get_labels(data)
    pool = numpy.array_split(labels, math.ceil(len(labels) / step))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("/annulla")
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
    if "presente" in res.text:
        return -1
    elif "Trying to get property 'ID' of non-object" in res.text:
        return -2
    return 0


async def delete_booking(lesson_id, username):
    params = {
        "mode": "cancella_prenotazioni",
        "codice_fiscale": username,
        "id_entries": f"[{lesson_id}]"
    }
    res = requests.get(API_URL, params=params)
    print(res.url)
    print(res.text)
    if "\{\}" in res.text:
        return -1
    return 0
