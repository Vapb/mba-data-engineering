import re
from lxml.html import fromstring
from unidecode import unidecode


def get_tree_from_url(session, url, cookies={}):
    response = session.get(url, cookies=cookies)
    return fromstring(response.text)


def extract_price(price):
    price = price.replace('/kg', '')
    return int(re.sub(r"\s|R|\$|,", "", price)) / 100


def extract_url_code(url):
    code_match = re.search(r'/(\d+)/$', url)
    code = code_match.group(1)
    return code


def process_text(text):
    text = unidecode(text)
    text = text.replace("'", "")
    text = text.replace(',', '')
    text = text.lower()
    return text