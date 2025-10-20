import logging
from DrissionPage import ChromiumPage, ChromiumOptions
import re
import time
import tempfile
import sys
import os
import json
import random
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('price_changer.parsers')

ua = UserAgent(browsers=['chrome', 'firefox', 'edge'], os=['windows', 'macos', 'linux'], platforms='pc')

# Путь для сохранения профиля браузера
PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'browser_profile')

def get_chromium_options():
    co = ChromiumOptions()

    # Базовые настройки для стабильности
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-gpu')
    
    # Реалистичные настройки браузера
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--disable-extensions')
    co.set_argument('--disable-software-rasterizer')
    co.set_argument('--disable-setuid-sandbox')
    co.set_argument('--window-size=1920,1080')
    co.set_argument('--start-maximized')
    
    # Отключаем различные функции, которые могут выдать бота
    co.set_argument('--disable-background-timer-throttling')
    co.set_argument('--disable-backgrounding-occluded-windows')
    co.set_argument('--disable-renderer-backgrounding')
    co.set_argument('--disable-back-forward-cache')
    co.set_argument('--disable-ipc-flooding-protection')
    co.set_argument('--disable-hang-monitor')
    co.set_argument('--disable-client-side-phishing-detection')
    co.set_argument('--disable-sync')
    co.set_argument('--no-first-run')
    co.set_argument('--safebrowsing-disable-auto-update')
    co.set_argument('--disable-default-apps')
    co.set_argument('--disable-prompt-on-repost')
    co.set_argument('--disable-domain-reliability')
    co.set_argument('--password-store=basic')
    co.set_argument('--use-mock-keychain')
    co.set_argument('--disable-component-update')
    
    # Скрываем автоматизацию
    co.set_argument('--exclude-switches=enable-automation')
    co.set_argument('--disable-features=UserAgentClientHint')
    co.set_argument('--remote-debugging-port=0')
    
    # Включаем WebGL и другие нормальные функции браузера
    co.set_argument('--enable-webgl')
    co.set_argument('--enable-accelerated-2d-canvas')
    co.set_argument('--enable-accelerated-mjpeg-decode')
    co.set_argument('--enable-gpu-rasterization')
    
    # Реалистичные настройки контента
    co.set_argument('--enable-native-gpu-memory-buffers')
    co.set_argument('--enable-viewport')
    co.set_argument('--enable-touchpad-differential-scrolling')
    
    # Язык и регион
    co.set_argument('--lang=ru-RU,ru;q=0.9,en;q=0.8')
    co.set_argument('--accept-lang=ru-RU,ru;q=0.9,en;q=0.8')
    
    # Headless режим (можно отключить для отладки)
    co.set_argument('--headless=new')
    
    # Используем постоянный профиль для сохранения cookies и сессий
    os.makedirs(PROFILE_PATH, exist_ok=True)
    co.set_argument(f'--user-data-dir={PROFILE_PATH}')
    
    # Отключаем блокировку изображений для большей реалистичности
    # co.no_imgs()  # Закомментировано для реалистичности
    
    # Устанавливаем реалистичный user-agent
    user_agent = get_realistic_user_agent()
    co.set_argument(f'--user-agent={user_agent}')
    
    return co

def get_realistic_user_agent():
    """Генерирует более реалистичный user-agent с учетом разных браузеров и ОС"""
    browsers = [
        lambda: ua.chrome,
        lambda: ua.firefox,
        lambda: ua.edge
    ]
    
    # Случайный выбор браузера
    browser_func = random.choice(browsers)
    user_agent = browser_func()
    
    # Добавляем случайные версии для большей реалистичности
    if 'Chrome' in user_agent:
        # Обновляем версию Chrome до более современной
        user_agent = re.sub(r'Chrome/\d+\.\d+\.\d+\.\d+', f'Chrome/{random.randint(110, 125)}.0.0.0', user_agent)
    
    return user_agent

def set_realistic_browser_properties(page):
    """Устанавливает реалистичные свойства браузера чтобы избежать обнаружения"""
    
    # Скрываем WebDriver свойства
    page.run_js('''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    ''')
    
    # Устанавливаем реалистичные свойства плагинов
    page.run_js('''
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    ''')
    
    # Устанавливаем реалистичные свойства languages
    page.run_js('''
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ru-RU', 'ru', 'en-US', 'en'],
        });
    ''')
    
    # Скрываем наличие automation
    page.run_js('''
        window.chrome = {
            runtime: {},
        };
    ''')
    
    # Устанавливаем реалистичную платформу
    page.run_js('''
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });
    ''')
    
    # Случайная задержка между действиями (имитация человеческого поведения)
    time.sleep(random.uniform(0.5, 2.0))

def gradual_scroll(page, scroll_pixels=1000, pause=1, max_scrolls=10):
    current_height = page.run_js('return document.documentElement.scrollHeight')
    
    for _ in range(max_scrolls):
        page.scroll.down(scroll_pixels)
        time.sleep(pause)

        new_height = page.run_js('return document.documentElement.scrollHeight')
        if new_height == current_height:
            break
        current_height = new_height

def save_login_state(page, site_name):
    """Сохраняет состояние логина для сайта"""
    state_file = os.path.join(PROFILE_PATH, f'{site_name}_login_state.json')
    login_state = {
        'url': page.url,
        'timestamp': time.time(),
        'cookies_count': len(page.cookies()),
        'user_agent': page.user_agent
    }
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(login_state, f, ensure_ascii=False, indent=2)

def check_login_state(site_name):
    """Проверяет, есть ли сохраненное состояние логина"""
    state_file = os.path.join(PROFILE_PATH, f'{site_name}_login_state.json')
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            # Проверяем, не устарело ли состояние (старше 7 дней)
            if time.time() - state['timestamp'] < 7 * 24 * 60 * 60:
                return True
        except:
            pass
    return False

def manual_login_if_needed(page, site_name, seller_url):
    """Функция для ручного логина, если требуется"""
    if not check_login_state(site_name):
        logger.info(f"Требуется ручной логин для {site_name}")
        logger.info(f"Открыта страница: {seller_url}")
        logger.info("Пожалуйста, выполните вход вручную в открывшемся браузере...")
        
        # Выходим из headless режима для ручного логина
        page.quit()
        
        # Перезапускаем браузер без headless режима
        co = get_chromium_options()
        co.remove_argument('--headless=new')  # Убираем headless режим
        page = ChromiumPage(addr_or_opts=co)
        
        # Устанавливаем реалистичные свойства
        set_realistic_browser_properties(page)
        
        page.get(seller_url)
        logger.info("Браузер открыт для ручного логина. После входа нажмите Enter в консоли...")
        input("После успешного логина нажмите Enter для продолжения...")
        
        # Сохраняем состояние логина
        save_login_state(page, site_name)
        
        # Закрываем браузер и перезапускаем в headless режиме
        page.quit()
        return True
    return False

def parse_from_ozon(art):
    co = get_chromium_options()
    page = None
    
    try:
        user_agent = get_realistic_user_agent()
        co.set_argument(f'--user-agent={user_agent}')
        
        page = ChromiumPage(addr_or_opts=co)
        page.set.user_agent(user_agent)
        
        # Устанавливаем реалистичные свойства браузера
        set_realistic_browser_properties(page)
        
        seller_url = f'https://www.ozon.ru/seller/{str(art)}'
        
        # Проверяем необходимость ручного логина
        if manual_login_if_needed(page, 'ozon', seller_url):
            # Пересоздаем страницу после ручного логина
            page = ChromiumPage(addr_or_opts=co)
            page.set.user_agent(user_agent)
            set_realistic_browser_properties(page)
        
        logger.info(f"Переходим на страницу продавца Ozon {art}")
        page.get(seller_url)
        
        # Реалистичная задержка перед началом взаимодействия
        time.sleep(random.uniform(2, 5))
        
        page.wait.load_start()
        page.wait.doc_loaded(timeout=60)
        
        # Дополнительная случайная задержка
        time.sleep(random.uniform(1, 3))
        
        # Проверяем, не перенаправило ли нас на страницу логина
        if 'login' in page.url.lower() or 'signin' in page.url.lower():
            logger.warning("Обнаружена страница логина. Требуется повторная аутентификация.")
            save_login_state(page, 'ozon')  # Сбрасываем состояние
            return None
        
        gradual_scroll(page, max_scrolls=15)
        logger.info("Прокрутка страницы завершена")

        # Случайная пауза после прокрутки
        time.sleep(random.uniform(1, 2))

        # [остальной код парсинга Ozon остается без изменений]
        block_selectors = [
            "xpath://div[contains(@class, 'tile-root')]",
            ".qi1_24.tile-root.wi5_24.wi6_24",
            'xpath://div[contains(@class, "qi1_24") and contains(@class, "tile-root") and contains(@class, "wi5_24") and contains(@class, "wi6_24"]',
        ]

        price_selectors = [
            "xpath://span[contains(@class, 'tsHeadline500Medium')]",
            ".c35_3_3-a1.tsHeadline500Medium.c35_3_3-b1.c35_3_3-a6",
            'xpath://span[contains(@class, "tsHeadline500Medium") and contains(@class, "c35_3_3-a1") and contains(@class, "c35_3_3-b1") and contains(@class, "c35_3_3-a6"]', 
        ]

        article_selectors = [
            "xpath://a[contains(@class, 'tile-clickable-element')]",
            ".q4b1_3_0-a.tile-clickable-element.iq7_24.qi7_24",
            'xpath://a[contains(@class, "tile-clickable-element") and contains(@class, "q4b1_3_0-a") and contains(@class, "iq7_24") and contains(@class, "qi7_24"]',
        ]
        
        result = {}
        block_elements = []

        for block_selector in block_selectors:
            try:
                page.wait.ele_displayed(block_selector, timeout=10)
                logger.info(f"Применен селектор {block_selector}")
                block_elements = page.eles(block_selector, timeout=10)
                if block_elements:
                    logger.info(f"Найдено {len(block_elements)} блоков товаров")
                    break
            except Exception as e:
                logger.info(f"Селектор {block_selector} не сработал: {e}")
                continue

        if not block_elements:
            logger.error("Не найдено ни одного блока товаров")
            return None
        
        for block_element in block_elements:
            price_element = None

            for price_selector in price_selectors:
                try:
                    price_element = block_element.ele(price_selector)
                    if price_element and price_element.text.strip():
                        break
                except:
                    continue
            
            if price_element:
                price_text = price_element.text.strip()
                price_with_discount_ozon = int(re.sub(r'\D', '', price_text))
            else:
                logger.info("Элемент с ценой в Ozon не найден")
                continue

            article_element = None
            for article_selector in article_selectors:
                try:
                    article_element = block_element.ele(article_selector).attr('href')
                    if article_element:
                        break
                except:
                    continue
            
            if article_element:
                article_match = re.search(r'(\d{10})', article_element)
                if article_match:
                    article_number = int(article_match.group(1))
                else:
                    article_match = re.search(r'(\d{9})', article_element)
                    article_number = int(article_match.group(1))
            else:
                logger.info("Элемент с артиклом в Ozon не найден")
                continue

            result[article_number] = price_with_discount_ozon
            
        return result

    except Exception as e:
        logger.error(f"Произошла ошибка при парсинге Ozon: {str(e)}")
        return None
    finally:
        if page:
            try:
                # Не закрываем браузер полностью, чтобы сохранить сессию
                page.tab_close()
            except:
                pass

def parse_from_wb(art):
    co = get_chromium_options()
    page = None
    
    try:
        user_agent = get_realistic_user_agent()
        logger.info(f"User Agent: {user_agent}")
        co.set_argument(f'--user-agent={user_agent}')
        
        page = ChromiumPage(addr_or_opts=co)
        page.set.user_agent(user_agent)
        
        # Устанавливаем реалистичные свойства браузера
        set_realistic_browser_properties(page)
        
        seller_url = f'https://www.wildberries.ru/seller/{str(art)}'
        
        # Проверяем необходимость ручного логина
        if manual_login_if_needed(page, 'wb', seller_url):
            # Пересоздаем страницу после ручного логина
            page = ChromiumPage(addr_or_opts=co)
            page.set.user_agent(user_agent)
            set_realistic_browser_properties(page)
        
        logger.info(f"Переходим на страницу продавца WB {art}")
        page.get(seller_url)
        
        # Реалистичная задержка перед началом взаимодействия
        time.sleep(random.uniform(2, 5))
        
        page.wait.load_start()
        page.wait.doc_loaded(timeout=60)
        
        # Дополнительная случайная задержка
        time.sleep(random.uniform(1, 3))
        
        # Проверяем, не перенаправило ли нас на страницу логина
        if 'login' in page.url.lower() or 'signin' in page.url.lower():
            logger.warning("Обнаружена страница логина. Требуется повторная аутентификация.")
            save_login_state(page, 'wb')  # Сбрасываем состояние
            return None
        
        gradual_scroll(page, max_scrolls=15)
        logger.info("Прокрутка страницы завершена")

        # Случайная пауза после прокрутки
        time.sleep(random.uniform(1, 2))

        # [остальной код парсинга WB остается без изменений]
        block_selectors = [
            "xpath://article[contains(@class, 'product-card') and contains(@class, 'j-card-item') and contains(@class, 'j-analitics-item')]",
            "xpath://article[contains(@class, 'product-card') and contains(@class, 'j-card-item')]",
            "xpath://article[contains(@class, 'product-card') and contains(@class, 'j-analitics-item')]",
            "xpath://article[contains(@class, 'product-card')]",
        ]

        price_selectors = [
            "xpath://ins[contains(@class, 'price__lower-price') and contains(@class, 'wallet-price') and contains(@class, 'red-price')]",
            "xpath://ins[contains(@class, 'price__lower-price') and contains(@class, 'wallet-price')]",
            "xpath://ins[contains(@class, 'wallet-price')]",
            "xpath://ins[contains(@class, 'price__lower-price')]",
        ]
        
        result = {}
        block_elements = []

        for block_selector in block_selectors:
            try:
                page.wait.ele_displayed(block_selector, timeout=10)
                logger.info(f"Применен селектор {block_selector}")
                block_elements = page.eles(block_selector, timeout=10)
                if block_elements:
                    logger.info(f"Найдено {len(block_elements)} блоков товаров")
                    break
            except Exception as e:
                logger.info(f"Селектор {block_selector} не сработал: {e}")
                continue

        if not block_elements:
            logger.error("Не найдено ни одного блока товаров")
            return None
        
        for block_element in block_elements:
            price_element = None

            for price_selector in price_selectors:
                try:
                    price_element = block_element.ele(price_selector)
                    if price_element and price_element.text.strip():
                        break
                except Exception as e:
                    logger.info(f"Не удалось найти цену: {e}")
                    continue
            
            if price_element:
                price_text = price_element.text.strip()
                price_with_discount_wb = int(re.sub(r'\D', '', price_text))
            else:
                logger.info("Элемент с ценой в WB не найден")
                continue

            article_element = None
            try:
                article_element = block_element.attr('data-nm-id')
            except Exception as e:
                logger.info(f"Не удалось получить артикул: {e}")
                continue
            
            if article_element:
                article_number = int(article_element.strip())
            else:
                logger.info("Элемент с артиклом в WB не найден")
                continue

            result[article_number] = price_with_discount_wb
            
        return result

    except Exception as e:
        logger.error(f"Произошла ошибка при парсинге WB: {str(e)}")
        return None
    finally:
        if page:
            try:
                # Не закрываем браузер полностью, чтобы сохранить сессию
                page.tab_close()
            except:
                pass