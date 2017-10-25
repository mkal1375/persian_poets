import urllib
import requests
from bs4 import BeautifulSoup
import time
import sqlite3

# connect to redis server :
# my_redis = redis.StrictRedis(host="localhost", port=6379, db=0)

################################################################################
### get data: ##################################################################
################################################################################

def create_tables():
    """
    create table for first use:
    poets table : |id|name|describe|infobox
    poems table : |id|poet_id|poem
    """
    try:
        db = sqlite3.connect("poets.db")
        cursor = db.cursor()
        cursor.execute(""" CREATE TABLE poets(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,describe TEXT,infobox TEXT,url Text)""")
        cursor.execute(""" CREATE TABLE poems(id INTEGER PRIMARY KEY AUTOINCREMENT,poet_id INTEGER,poem TEXT,FOREIGN KEY(poet_id) REFERENCES poets(id)) """)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise  e
    finally:
        db.close()

def insert_data(name , data):
    input_tuple = (name,str(data[0]),str(data[2]),str(data[3]))
    input_poems = data[1]
    def insert_poems(poet_id):
        try: 
            for poem in input_poems:                
                print("insert poem . . .")
                cursor.execute(""" INSERT INTO poems(poet_id,poem) VALUES(?,?) """,(poet_id,poem.text))
            db.commit()
        except Exception as e:
            db.rollback()
            db.close()
            raise e
        
    try:
        db = sqlite3.connect("poets.db")
        cursor = db.cursor()
        cursor.execute(""" INSERT INTO poets(name,describe,infobox,url) VALUES(?,?,?,?) """,input_tuple)
        print("poet data inserted .")
        poet_id = cursor.lastrowid
        insert_poems(poet_id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    print("     اطلاعات در دیتابیس ذخیره شد.")
    


def create_soup(page_url):
    """
    create a soup object from input url
    input : url (str)
    output : soup (soup objrect)

    """
    root_page = requests.get(page_url)
    return BeautifulSoup(root_page.text, "html.parser")


def clean_list(input_list):
    """
    1)clean scaraped data : delete [1], . . . 
    2)delete items without page
            normal items : https://fa.wikipedia.org/wiki/%D9%81%D8%B1%D8%AF%D9%88%D8%B3%DB%8C
            items without page :  https://fa.wikipedia.org/w/index.php?title=%D9%85%D8%B9%D9%86%D9%88%DB%8C%DB%8C_%D8%A8%D8%AE%D8%A7%D8%B1%D8%A7%DB%8C%DB%8C&action=edit&redlink=1
            these have 'index' in url
    input : list (soup object)
    output : list (soup object)

    # TODO: add numeric value
    """
    return [x for x in input_list if all(["[" not in x.text, 'index' not in x['href']])]


def get_poet(page_url):
    """
    get poet and scrape data : poems and personal data 
    input:	poet url (string)
    output:	poet details (tupel)
    """
    print("geting poet data . . .")
    def get_info_box(poet_soup):
        """
        get info box : wikipedia have dirty code. somewhere used .infobox and somewhere use .vcard class
        """
        if poet_soup.select(".infobox")!= None:
            return poet_soup.select(".infobox")
        elif poet_soup.select(".vacrd") != None:
            return poet_soup.select(".vacrd")
        else : return None
        
    # create soup object:
    soup = create_soup(page_url)
    # scrape data :
    try:
        info_box = get_info_box(soup)[0]
    except:
        info_box = None
    if info_box != None:
        info_box_text = info_box.text
    else:
        info_box_text = None
    #delete info box form tree : confilict by describe element
    if info_box != None:
        _ = info_box.extract()    
    describe = soup.select("#bodyContent p:nth-of-type(1)")[0].text
    poems = soup.select(".poem")
    for poem in poems:
        beyt = poem.select("td")
        for b in beyt:
            if b.text == "":
                b.string = "\n"
    return (describe,poems, info_box_text, page_url)

################################################################################
### main part: #################################################################
################################################################################
# create_tables()
# """
# crate soup from main page:
root_soup = create_soup("https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D8%A7%D8%B9%D8%B1%D8%A7%D9%86_%D9%81%D8%A7%D8%B1%D8%B3%DB%8C%E2%80%8C%D8%B2%D8%A8%D8%A7%D9%86")
# scrape data from clean list by css selector
poets_list = clean_list(root_soup.select("h2 + ul li + li a , .new , h4 + ul a"))

poets_dict = {}
# crate dictonary from list: merge url and name toghether
for poet in poets_list:
    poets_dict[poet.text] = urllib.parse.urljoin("https://fa.wikipedia.org/", poet['href'])

poets_temp = {}
for poet,link in poets_dict.items():
    print("درحال دریافت : ",poet)
    poets_temp[poet] = get_poet(link)
    insert_data(poet,poets_temp[poet])
    time.sleep(1)
poets_dict = poets_temp
# """
"""
TODO:
2)process on infobox
"""