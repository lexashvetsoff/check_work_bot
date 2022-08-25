import requests
import os
from dotenv import load_dotenv
import telegram
import time
import logging


logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot
    
    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    load_dotenv()

    tg_bot_token = os.environ['TOKEN_TG_BOT']
    chat_id = os.environ['TG_CHAT_ID']

    bot = telegram.Bot(tg_bot_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))

    logger.warning('Бот запущен!')

    devman_token = os.environ['TOKEN_DEVMAN_API']
    url_long_polling = 'https://dvmn.org/api/long_polling/'

    headers = {
        'Authorization': f'Token {devman_token}'
    }

    payload = {}

    while True:

        try:
            response = requests.get(url_long_polling, headers=headers, params=payload, timeout=90)
            response.raise_for_status()
            check_result = response.json()

            if check_result['status'] == 'timeout':
                payload['timestamp'] = check_result['timestamp_to_request']
            else:
                payload['timestamp'] = check_result['last_attempt_timestamp']

                result_work = check_result['new_attempts'][0]
                check_text = 'Преподаватель проверил работу!'
                lesson_title = result_work['lesson_title']
                if result_work['is_negative']:
                    status_text = 'К сожалению в работе выявлены недостатки :('
                else:
                    status_text = 'Работа принята! Можно приступать к следующему заданию :)'
                lesson_url = result_work['lesson_url']
                link_on_work = f'Поробности можно посмотреть по ссылке - {lesson_url}'
                message_text = f'{check_text} \n{lesson_title} \n{status_text} \n\n{link_on_work}'
                bot.send_message(text=f'{message_text}', chat_id=chat_id)
        except requests.exceptions.ConnectionError:
            logger.exception()
            logger.warning('Соединение разорвано!')
            logger.warning('Повторный запрос...')
            time.sleep(30)
        except requests.exceptions.ReadTimeout:
            pass
        except Exception:
            logger.exception()


if __name__ == '__main__':
    main()
