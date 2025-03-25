import logging


from app.common_log import configure_logging
from app.database import engine
from parser import fetch_bulletins, download_file
from process_spimex_files import process_downloaded_files

configure_logging(level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    # Сначала загружаем все бюллетени
    page = 1
    while True:
        log.info(f"Получение страницы {page}...")
        bulletins = fetch_bulletins(page)
        if not bulletins:
            log.info("Больше нет бюллетеней или достигнута запланированная дата.")
            break
        for bulletin in bulletins:
            log.info(f"Бюллетень: {bulletin['filename']} (Дата: {bulletin['date']})")
            download_file(bulletin["url"], bulletin["filename"])

        page += 1

    # Затем обрабатываем все загруженные файлы
    process_downloaded_files(engine)
    log.info("Обработка всех файлов завершена")


if __name__ == "__main__":
    main()
