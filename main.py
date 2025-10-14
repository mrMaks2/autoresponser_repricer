from apscheduler.schedulers.blocking import BlockingScheduler
from auto_responser.tasks import response_to_reviews
from repricer.tasks import change_price
from campaigns.tasks_true import campaigns_placement_redact as placement_true
from campaigns.tasks_false import campaigns_placement_redact as placement_false
import logging
import random
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

def change_price_random_interval():
    """Запускает change_price и планирует следующий запуск со случайным интервалом"""
    # Выполняем основную задачу
    change_price()
    
    # Генерируем случайный интервал от 10 до 20 минут
    next_interval = random.randint(10, 20)
    
    # УДАЛЯЕМ старую задачу перед созданием новой
    scheduler.remove_job('change_price_job')
    
    # Создаем новую задачу со случайным интервалом
    scheduler.add_job(
        change_price_random_interval, 
        "interval", 
        minutes=next_interval,
        id='change_price_job'
    )
    
    logger.info(f"Следующий запуск change_price через {next_interval} минут")

if __name__ == "__main__":
    response_to_reviews()
    change_price()
    placement_true()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(response_to_reviews, "interval", minutes=15)
    scheduler.add_job(placement_true, "interval", minutes=15)
    scheduler.add_job(placement_false, "interval", seconds=62)
    
    # Первый запуск change_price со случайным интервалом
    first_interval = random.randint(10, 20)
    scheduler.add_job(
        change_price_random_interval, 
        "interval", 
        minutes=first_interval,
        id='change_price_job'
    )

    try:
        logger.info("[+] Запустился планировщик")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Планировщик остановлен")
        pass
    except Exception as e:
        logger.error(f"Ошибка в планировщике: {e}")