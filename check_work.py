import requests
import os
from dotenv import load_dotenv
import telegram
import time


def main():
    load_dotenv()

    tg_bot_token = os.getenv('TOKEN_TG_BOT')
    chat_id = os.getenv('TG_CHAT_ID')

    bot = telegram.Bot(tg_bot_token)

    devman_token = os.getenv('TOKEN_DEVMAN_API')
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
            print('Соединение разорвано!')
            print('Повторный запрос...')
            time.sleep(30)
        except requests.exceptions.ReadTimeout:
            print('Что то пошло не так!')
            time.sleep(90)
            print('Повторный запрос...')


if __name__ == '__main__':
    main()
