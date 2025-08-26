from apscheduler.schedulers.blocking import BlockingScheduler
from auto_responser.tasks import response_to_reviews
from repricer.tasks import change_price
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tasks')


if __name__ == "__main__":
    response_to_reviews()
    change_price()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(response_to_reviews, "interval", minutes=15)
    scheduler.add_job(change_price, "interval", minutes=15)

    try:
        logger.info("[+] Запустился планировщик")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Планировщик остановлен")
        pass
    except Exception as e:
        logger.error(f"Ошибка в планировщике: {e}")