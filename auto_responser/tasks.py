import requests
import os
from dotenv import load_dotenv
from random import randint
import logging
import ast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tasks')

load_dotenv()
jwt_for_resp_and_get_cab1 = os.getenv('jwt_for_resp_and_get_cab1')
jwt_for_resp_and_get_cab2 = os.getenv('jwt_for_resp_and_get_cab2')
jwt_for_resp_and_get_cab3 = os.getenv('jwt_for_resp_and_get_cab3')
url_for_reviews = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
url_for_response = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer'

def load_dict_from_file(filename):
    """Загружает словарь из текстового файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return ast.literal_eval(content)
            else:
                return {}
    except (FileNotFoundError, SyntaxError, ValueError) as e:
        logger.error(f"Ошибка загрузки файла {filename}: {e}")
        return {}
    
response_list_cab3 = load_dict_from_file('auto_responser/response_list_cab3.txt')

with open('auto_responser/response_list_cab1_2.txt', 'r', encoding='utf-8') as f:
        response_list_cab1_2 = [str(resp.strip().strip('"')) for resp in f.readlines()]

params_reviews = {
    "isAnswered": 'false',
    "take": 5000,
    "skip": 0
}

headers_cab1 = {
    'Authorization': jwt_for_resp_and_get_cab1
}

headers_cab2 = {
    'Authorization': jwt_for_resp_and_get_cab2
}

headers_cab3 = {
    'Authorization': jwt_for_resp_and_get_cab3
}

headers_list = [headers_cab1, headers_cab2, headers_cab3]

def response_to_reviews():

    for headers in headers_list:

        if headers['Authorization'] == jwt_for_resp_and_get_cab3:

            try:
                response = requests.get(url_for_reviews, headers=headers, params=params_reviews, timeout=30)
                response.raise_for_status()
                
                reviews_data = response.json()
                
                if not reviews_data.get('data') or not reviews_data['data'].get('feedbacks'):
                    logger.warning("Нет отзывов для обработки или неверная структура ответа")
                    return

                ids = {}

                for review in reviews_data['data']['feedbacks']:
                    if review.get('productValuation') == 5:
                        reviews_id = review.get('id')
                        reviews_nmid = review.get('productDetails', {}).get('nmId')
                        if reviews_id and reviews_nmid:
                            ids[reviews_id] = reviews_nmid

                logger.info(f"Найдено отзывов для ответа: {len(ids)}")

                for review_id, review_nmid in ids.items():
                    try:
                        response_list_nmid = response_list_cab3.get(review_nmid)
                        if not response_list_nmid:
                            logger.info(f'Не найден шаблон ответа для nmId: {review_nmid}')
                            continue
                        
                        resp_len = len(response_list_nmid)
                        if resp_len == 0:
                            logger.warning(f'Пустой список ответов для nmId: {review_nmid}')
                            continue

                        params_response = {
                            "id": review_id,
                            "text": response_list_nmid[randint(0, resp_len - 1)]
                        }

                        logger.info(f"Отправка ответа на отзыв {review_id}: {params_response['text'][:50]}...")
                        
                        resp = requests.post(url_for_response, headers=headers, json=params_response, timeout=30)
                        resp.raise_for_status()
                        logger.info(f"Успешно ответили на отзыв {review_id}")

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Ошибка при отправке ответа на отзыв {review_id}: {e}")
                    except Exception as e:
                        logger.error(f"Неожиданная ошибка при обработке отзыва {review_id}: {e}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при получении отзывов: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка в функции response_to_reviews: {e}")

        else:
                
            try:

                response = requests.get(url_for_reviews, headers=headers, params=params_reviews)
                response.raise_for_status()

                reviews_data = response.json()

                if not reviews_data.get('data') or not reviews_data['data'].get('feedbacks'):
                    logger.warning("Нет отзывов для обработки или неверная структура ответа")
                    continue

                ids = []

                for review in reviews_data['data']['feedbacks']:
                    if review['productValuation'] == 5:
                        review_id = review['id']
                        ids.append(review_id)

                logger.info(f"Найдено отзывов для ответа: {len(ids)}")

                for review_id in ids:
                    try:
                        params_response = {
                            "id": review_id,
                            "text": response_list_cab1_2[randint(0,38)]
                        }
                        logger.info(f"Отправка ответа на отзыв {review_id}: {params_response['text'][:50]}...")
                        requests.post(url_for_response, headers=headers, json=params_response)

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Ошибка при отправке ответа на отзыв {review_id}: {e}")
                    except Exception as e:
                        logger.error(f"Неожиданная ошибка при обработке отзыва {review_id}: {e}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при получении отзывов: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка в функции response_to_reviews: {e}")
                