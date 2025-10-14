import requests
import os
from dotenv import load_dotenv
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('campaigns.tasks_false')

load_dotenv()
token_for_campaigns = os.getenv('token_for_campaigns')

url_for_campaigns = 'https://advert-api.wildberries.ru/adv/v0/auction/placements' #PUT

def campaigns_placement_redact():

    headers = {
        'Authorization': token_for_campaigns
    }
    
    params = {
        "placements": [
            {
                "advert_id": 29207976,
                "placements": {
                    "search": False,
                    "recommendations": True
                }
            }
        ]
    }

    response = requests.put(url_for_campaigns, headers=headers, json=params)

    if response.status_code != 204:
        logger.info(f'Не получилось изменить статус на False с кодом {response.status_code}')
        return True
    
    logger.info('Статус успешно изменен на False')
    return True