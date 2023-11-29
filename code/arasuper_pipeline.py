import os
from dotenv import load_dotenv
from datetime import datetime
from requests import Session
from time import sleep
from tools_utils import get_tree_from_url
from tools_utils import extract_price
from tools_utils import extract_url_code
from tools_utils import process_text
from db import PostgreSQLConnection


# Add argparsers

# Base variables
BASE_URL = 'https://www.arasuper.com.br/'
BASE_MKP =  7
# Departments xpaths
ALL_DEPS = (
    '//ul[@class="menu-principal__items menu-principal__col menu-principal__col--1"]'
)
DEP_NAME = 'a/span/span'
DEP_URL = 'a/@href'
SUB_DEPS = 'div/div/ul/li' 
# Products xpaths
PRODUCT_NAME = 'div/div[3]/div/p[@class="item-produto__name"]'
PRODUCT_BRAND = 'div/div[3]/div/p[@class="item-produto__brand"]'
PRICE_ONE = 'div/div[3]/div/p[@class="item-produto__price just-one"]'
PRICE_TWO = 'div/div[3]/div/p[@class="item-produto__price"]'
PRICE_LEVE = 'div/div[3]/div/p[@class="item-produto__price price-leve"]'
PRICE_REGULAR = 'span[@class="item-produto__price-de"]'
PRICE = 'span[@class="item-produto__price-por"]'
PRODUCTS =  '//div[@class="products-list"]/a'


def get_departments(session):
    """
    Extract all departments from BASE_URL
    """
    department = {}
    tree = get_tree_from_url(session, BASE_URL)
    for dep in tree.xpath(ALL_DEPS)[1]:
        depName = dep.xpath(DEP_NAME)[0].text_content()    
        subDeps = dep.xpath(SUB_DEPS)
        
        # Subdepartments Exists
        if subDeps != []:
            for sub in subDeps:
                subcontent = sub.text_content().split()
                if not(subcontent in [['Todos'],['Voltar']]):
                    subName = sub.xpath(DEP_NAME)[0].text_content()
                    department["url"] = BASE_URL + sub.xpath(DEP_URL)[0]
                    department["hierarchy"] = process_text(depName + ' > ' + subName)
                    department["id"] = f"ARA_{extract_url_code(department["url"])}"
                    yield department
        
        else:
            department["url"] = BASE_URL + dep.xpath(DEP_URL)[0]
            department["hierarchy"] = process_text(depName)
            department["id"] = f"ARA_{extract_url_code(department["url"])}"
            yield department


def get_pages(session, department_url):
    """
    Get all pages from a departmente given an department_url
    """
    i = 1
    while True:
        new_url = department_url + '?page=' + str(i)
        tree = get_tree_from_url(session, new_url)
        page_empty = tree.xpath('//div[@class="produto-lista empty-content"]')
        if page_empty != []:
            break
        else:
            yield tree
        i = i + 1
 

def extract_products(page):
    products_info = []
    for product in page.xpath(PRODUCTS): 
        product_url = BASE_URL + product.xpath('@href')[0]
        product_sku = f"ARA_{extract_url_code(product_url)}"
        product_name = process_text(product.xpath(PRODUCT_NAME)[0].text_content())
        product_brand = process_text(product.xpath(PRODUCT_BRAND)[0].text_content())
        
        if product.xpath(PRICE_ONE): # One price
            regular_price = product.xpath(PRICE_ONE)[0].text_content()
            regular_price = extract_price(regular_price)
            price = "NULL"
            
        elif product.xpath(PRICE_TWO): # Regular Price and Price
            prices = product.xpath(PRICE_TWO)[0]
            regular_price = prices.xpath(PRICE_REGULAR)[0].text_content()
            regular_price = extract_price(regular_price)
            price = prices.xpath(PRICE)[0].text_content()
            price = extract_price(price)
        
        else: # Only price
            prices = product.xpath(PRICE_LEVE)[0]
            regular_price = prices.xpath(PRICE_REGULAR)[0].text_content()
            regular_price = extract_price(regular_price)
            price = "NULL"

        # INSERT PRODUCT IN TABLE
        products_info.append(
            {
                'sku': product_sku,
                'url': product_url,
                'name': product_name,
                'brand': product_brand,
                'price': price,
                'regular_price': regular_price
            }
        )
    return products_info


def main():
    collection_date = datetime.now()
    session = Session()
    conn = PostgreSQLConnection(
        dbname="postgres",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    conn.connect()
    for department in get_departments(session):
        print('INSERT DEP : ', department)
        conn.insert_department(
            department['id'], department['url'], department["hierarchy"]
        )
        for page in get_pages(session, department['url']):
            products = extract_products(page)
            for product in products:
                print("INSERT Product : ", product)
                conn.insert_product(product['sku'], product["name"], product["brand"])
                conn.insert_advertisement(
                    BASE_MKP,
                    department['id'],
                    product['sku'],
                    product['price'],
                    product['regular_price'],
                    collection_date
                )
            sleep(5) # 10 Seconds for Page   
    conn.close_connection()
    return None


load_dotenv()
main()