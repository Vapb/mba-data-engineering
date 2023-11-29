import os
from dotenv import load_dotenv
from datetime import datetime
from time import sleep
from re import findall
from math import ceil
from requests import Session
from tools_utils import process_text
from tools_utils import get_tree_from_url
from tools_utils import extract_price
from db import PostgreSQLConnection


# Global vars
BASE_URL = 'https://www.comper.com.br/'
TOKEN_URL = "https://www.comper.com.br:443/api/sessions/"
DEPS_URL = "https://www.comper.com.br/api/catalog_system/pub/category/tree/3/"
PAGINATION = '//script[contains(text(), "window.location.hash = pageclickednumber")]'
PAGINATION_URL = "\$\('\#ResultItems_%s'\).load\('(?P<a>[^']+)'"
PAGE_COUNT = 'pagecount_%s = (?P<a>\d+);'

PRODUCTS = '//div[@class="shelf-item"]'
PRODUCT_NAME = 'div/h3[@class="shelf-item__title"]/a'
PRODUCT_BRAND = 'div/div[@class="shelf-item__brand"]/a'
PRODUCT_URL = 'div/h3/a/@href'
PRICE_REGULAR = 'div/div/div/span[@class="shelf-item__list-price"]'
PRICE = 'div/div/div/span/div/div/strong'

# All store codes
store_code = {
    "MT": 1,   #Cuiabá
    "MS": 2,   #CampoGrande
    "DF": 3,   #Brasília - Águas Claras
    "DF2": 4,  #Brasília - Sobradinho
    "MS2": 5,  #Dourados
    "MT2": 6,  #Rondonopolis
}


def set_token(session, store_id):
    """
    Set tokens for webscrapping session
    """
    session.get(url=f"https://www.comper.com.br:443/Site/Track.aspx?sc={store_id}")
    token_json={"public":{}}
    session.post(TOKEN_URL, cookies=session.cookies, json=token_json)
    tokens = session.cookies.get_dict()
    return tokens 
    

def get_json_deps(session):
    """
    Get json departments
    """
    json_response = session.get(DEPS_URL).json()
    return json_response


def get_departments(session):
    department = {}
    for dep in get_json_deps(session):
        dep_name = dep['name']
        
        # Subdepartments Exists
        if (dep['hasChildren']) and (dep['children'] != []):
            for sub_dep in dep['children']:
                sub_dep_name = sub_dep['name']
                department['hierarchy'] = process_text(f"{dep_name} > {sub_dep_name}")
                department['url'] = sub_dep['url'].replace('.vtexcommercestable.', '')
                department['id'] = f"COMP_{sub_dep['id']}"
                yield department
                       
        else:
            department['hierarchy'] = process_text(f"{dep_name}")
            department['url'] = dep['url'].replace('.vtexcommercestable.', '')
            department['id'] = f"COMP_{dep['id']}"
            yield department  
    


def get_pagination(tree):
    try:
        pager_element = tree.xpath('//div[@class="pager top"]')[0]
    except IndexError:
        return None, None
    
    pager_id = pager_element.attrib['id'].split('_')[1]
    pagination_script = tree.xpath(PAGINATION)[0]
    script = pagination_script.text
    page_count = findall(PAGE_COUNT % pager_id, script)
    page_count = int(page_count[0])
    pagination_url = findall(PAGINATION_URL % pager_id, script)[0]
    pagination_url = pagination_url.replace('PS=32', 'PS=50')
    total_products = 32 * page_count
    page_count = ceil(total_products/50)
    return page_count, pagination_url


def get_pages(session, department_url, cookies):
    tree = get_tree_from_url(session, department_url, cookies=cookies)
    max_pages, pagination_url = get_pagination(tree)
    if max_pages == None:
        return []
    for i in range(1, max_pages + 1):
        product_page =  BASE_URL + pagination_url + str(i)
        try:
            print(product_page)
            yield get_tree_from_url(session, product_page, cookies=cookies)
        except:
            break


def extract_products(page):
    products_info = []
    for item in page.xpath(PRODUCTS):
        product_url = item.xpath(PRODUCT_URL)[0]        
        product_sku = f"COMP_{item.xpath('@data-product-id')[0]}"
        product_name = process_text(item.xpath(PRODUCT_NAME)[0].text)
        product_brand = process_text(item.xpath(PRODUCT_BRAND)[0].text)

        # Check if product is unavailable
        if (len(item.xpath(PRICE_REGULAR)) == 0) and (len(item.xpath(PRICE)) == 0):
            continue
            
        else:
            second_price = item.xpath(PRICE_REGULAR)[0].text.strip()
            main_price = item.xpath(PRICE)[0].text.strip()          
            if second_price != '':
                regular_price = extract_price(second_price)
                best_price = extract_price(main_price)
            else:
                regular_price = extract_price(main_price)
                best_price = "NULL"

        products_info.append(
            {
                'sku' : product_sku,
                'url': product_url,
                'name': product_name,
                'brand': product_brand,
                'price': best_price,
                'regular_price': regular_price
            }
        )
    return products_info


def main(store_id):
    collection_date = datetime.now()
    session = Session()
    conn = PostgreSQLConnection(
        dbname="postgres",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    conn.connect()
    tokens = set_token(session, store_id)
    for department in get_departments(session):
        print('DEP: ', department)
        conn.insert_department(
            department['id'], department['url'], department["hierarchy"]
        )
        for page in get_pages(session, department['url'], tokens):
            products = extract_products(page)
            if len(products) == 0:
                break
            for product in products:
                print(product) 
                conn.insert_product(product['sku'], product["name"], product["brand"])
                conn.insert_advertisement(
                    store_id,
                    department['id'],
                    product['sku'],
                    product['price'],
                    product['regular_price'],
                    collection_date
                )
            sleep(30) # 30 Seconds for Page
    conn.close_connection()
    return None



load_dotenv()
main(store_code["MT"])