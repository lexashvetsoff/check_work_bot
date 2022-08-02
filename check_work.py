import requests
import os
from dotenv import load_dotenv
import asyncio
import telegram


def fetch_devman(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


async def main():
    load_dotenv()

    token_tg_bot = os.getenv('TOKEN_TG_BOT')
    chat_id = os.getenv('CHAT_ID')

    bot = telegram.Bot(token_tg_bot)

    token_dvm = os.getenv('TOKEN_DEVMAN_API')
    url_long_polling = 'https://dvmn.org/api/long_polling/'

    headers = {
        'Authorization': f'Token {token_dvm}'
    }

    payload = {}

    while True:

        try:
            answer = fetch_devman(url_long_polling, headers, payload)

            if answer['status'] == 'timeout':
                payload['timestamp'] = answer['timestamp_to_request']
            else:
                payload['timestamp'] = answer['last_attempt_timestamp']

                result_work = answer['new_attempts'][0]
                check_text = 'Преподаватель проверил работу!'
                lesson_title = result_work['lesson_title']
                if result_work['is_negative']:
                    status_text = 'К сожалению в работе выявлены недостатки :('
                else:
                    status_text = 'Работа принята! Можно приступать к следующему заданию :)'
                lesson_url = result_work['lesson_url']
                link_on_work = f'Поробности можно посмотреть по ссылке - {lesson_url}'
                message_text = f'{check_text} \n{lesson_title} \n{status_text} \n\n{link_on_work}'
                async with bot:
                    await bot.send_message(text=f'{message_text}', chat_id=chat_id)
        except requests.exceptions.ConnectionError:
            print('Соединение разорвано!')
            print('Повторный запрос...')
        except requests.exceptions.ReadTimeout:
            print('Что то пошло не так!')
            print('Повторный запрос...')


if __name__ == '__main__':
    asyncio.run(main())
