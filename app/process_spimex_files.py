import logging
import os
import re

import pandas as pd

from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from database import Spimex, engine

log = logging.getLogger(__name__)

DOWNLOAD_DIR = './downloads'

def safe_float_conversion(value):
    try:
        return float(Decimal(str(value)))
    except:
        return 0.0


def prepare_data(df):
    # Находим начало таблицы "Метрическая тонна"
    start_idx = df[df.iloc[:, 1].str.contains('Единица измерения: Метрическая тонна', na=False)].index[0]
    data = df.iloc[start_idx + 2:].copy()
    data.columns = df.iloc[start_idx + 1].values

    # Обработка числовых полей
    data['Объем\nДоговоров\nв единицах\nизмерения'] = data['Объем\nДоговоров\nв единицах\nизмерения'].apply(
        safe_float_conversion)
    data['Обьем\nДоговоров,\nруб.'] = data['Обьем\nДоговоров,\nруб.'].apply(safe_float_conversion)
    data['Количество\nДоговоров,\nшт.'] = data['Количество\nДоговоров,\nшт.'].replace('-', '0').apply(
        safe_float_conversion)

    return data[data['Количество\nДоговоров,\nшт.'] > 0]


def insert_to_db(engine, data, file_data):
    with Session(engine) as session:
        for _, row in data.iterrows():
            try:
                # Проверка и преобразование данных
                if not isinstance(row['Код\nИнструмента'], str):
                    continue

                spimex = Spimex(
                    exchange_product_id=str(row['Код\nИнструмента']),
                    exchange_product_name=str(row['Наименование\nИнструмента']),
                    oil_id=str(row['Код\nИнструмента'])[:4],
                    delivery_basis_id=str(row['Код\nИнструмента'])[4:7],
                    delivery_basis_name=str(row['Базис\nпоставки']),
                    delivery_type_id=str(row['Код\nИнструмента'])[-1],
                    volume=safe_float_conversion(row['Объем\nДоговоров\nв единицах\nизмерения']),
                    total=safe_float_conversion(row['Обьем\nДоговоров,\nруб.']),
                    count=safe_float_conversion(row['Количество\nДоговоров,\nшт.']),
                    date=file_data,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(spimex)
            except Exception as e:
                log.error(f"Ошибка в строке {row}: {str(e)}")
                continue

        try:
            session.commit()
            log.info(f"Успешно добавлено {len(data)} записей")
        except Exception as e:
            session.rollback()
            log.error(f"Ошибка при коммите: {str(e)}")


def process_downloaded_files(engine):
    """Обрабатывает все загруженные файлы в директории DOWNLOAD_DIR"""
    xls_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.xls')]

    if not xls_files:
        log.info("Не найдено XLS-файлов для обработки")
        return

    log.info(f"Найдено {len(xls_files)} файлов для обработки")

    for file_name in xls_files:
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        try:
            # Извлекаем дату из имени файла
            date_str = file_name[:10]
            trade_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            log.info(f"Обработка файла: {file_name} (дата: {trade_date})")
            df = pd.read_excel(file_path, sheet_name='TRADE_SUMMARY')
            filtered_data = prepare_data(df)

            if not filtered_data.empty:
                insert_to_db(engine, filtered_data, trade_date)
            else:
                log.warning(f"Нет данных для вставки в файле {file_name}")

        except Exception as e:
            log.error(f"Ошибка при обработке файла {file_name}: {e}")

