import requests
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tasks')

load_dotenv()
jwt_for_img = os.getenv('jwt_for_img')

url = "https://content-api.wildberries.ru/content/v3/media/file"

headers = {
    "Authorization": jwt_for_img,
    "X-Nm-Id": "16144458",  # Артикул WB
    "X-Photo-Number": "1"   # Номер медиафайла (начинается с 1)
}

def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.counter += 1
        # Передаем счетчик как дополнительный аргумент
        return func(wrapper.counter, *args, **kwargs)
    wrapper.counter = 0
    return wrapper

@count_calls
def img_changer(call_count):
    # Укажите абсолютный путь к файлу на вашем компьютере
    file_path = r"C:\autoresponser_repricer\img_changer\imgs\16144458_{call_count}.jpg"
    file_path = file_path.format(call_count=call_count)

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return

    try:
        with open(file_path, 'rb') as file:
            files = {
                'uploadfile': (os.path.basename(file_path), file, 'image/jpeg')
            }
            
            response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                logger.info("Изображение успешно загружено")
            else:
                logger.error(f"Ошибка загрузки: {response.text}")
                
    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения: {e}")
