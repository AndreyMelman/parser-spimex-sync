import logging

import requests
import os

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import certifi
from datetime import datetime

log = logging.getLogger(__name__)

BASE_URL = "https://spimex.com/markets/oil_products/trades/results/"
DOWNLOAD_DIR = "downloads/"
TARGET_DATE = datetime(2023, 1, 1)  # Устанавливаем дату, до которой нужно парсить


os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def fetch_bulletins(page):
    url = f"{BASE_URL}?page=page-{page}&bxajaxid=d609bce6ada86eff0b6f7e49e6bae904"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        bulletins = []

        items = soup.select(".accordeon-inner__item")
        for item in items:
            link = item.select_one("a.accordeon-inner__item-title.link.xls")
            date_element = item.select_one(".accordeon-inner__item-inner__title span")

            if link and date_element:
                url = urljoin(BASE_URL, link["href"])
                trade_date = datetime.strptime(date_element.text.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")

                # Если встретили дату меньше целевой, останавливаем
                if datetime.strptime(trade_date, "%Y-%m-%d") < TARGET_DATE:
                    log.info(f"Достигнутая целевая дата {TARGET_DATE}, стоп.")
                    return []

                filename = f"{trade_date}.xls"
                bulletins.append({"url": url, "filename": filename, "date": trade_date})
        return bulletins

    except Exception as e:
        log.error(f"Ошибка при получении страницы {page}: {e}")
        return []

def download_file(url, filename):
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        log.info(f"Загрузка завершена: {filepath}")
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка загрузки файла {filename}: {e}")
