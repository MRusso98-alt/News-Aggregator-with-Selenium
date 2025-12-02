import json
from collections import defaultdict
from datetime import datetime
import time as t
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#lista di tutti i siti in cui cercare
LIST_OF_SITES:list = ["https://www.repubblica.it/", "https://www.ilgiornale.it/", "https://www.ilfattoquotidiano.it/", "https://www.lastampa.it/", "https://www.ilmessaggero.it/"]
#lista dei nomi di tutti i siti
SITE_NAMES:list = ["La Repubblica", "Il Giornale", "Il Fatto Quotidiano", "La Stampa", "Il Messaggero"]
NUM_OF_ENTRIES:int = 3 #quanti elementi prendere da ogni sito
JSON_URL:str = "articoli.json" #nome del file di destinazione JSON

options = Options() #opzioni Selenium
options.add_argument("--start-maximized") #inizia a schermo intero
options.add_argument("--headless")

def write_to_json(data, path_json):
    old_data = json.load(open(path_json))
    new_data = old_data | data
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4)

def scrape_repubblica(url:str, nome:str, prompt:list, driver):
    driver.get(url) #vai alla pagina
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "iubenda-cs-accept-btn"))).click() #clicca su cookie
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "repSearchToggleButton"))).click() #apri search

    search = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[3]/div/form/input[1]'))) #trova search bar
    search.click()
    search.clear()

    for i in prompt:
        search.send_keys(i)
        search.send_keys(" ")

    search.send_keys(Keys.RETURN)
    #clicca, ripulisci input, aggiungi keyword e invia

    t.sleep(2)
    dati_articoli:dict = defaultdict(dict) #inizializza diz vuoto

    for i in range(NUM_OF_ENTRIES):
        try:
            articoli = driver.find_elements(By.CLASS_NAME, "block__item")  # lista di tutti gli articooli
        except:
            if i == 0:
                print("Nessun articolo trovato con questo input")
            return

        articolo = "articolo " + str(i+1) #crea stringa di ID articolo

        if (i >= len(articoli)):
            return

        dati_articoli[nome][articolo] = defaultdict(dict) #inizializza dizionario innestato vuoto

        titolo = articoli[i].find_element(By.CLASS_NAME, "entry__title")
        url = titolo.find_element(By.XPATH, "./*")
        dati_articoli[nome][articolo]["titolo"] = titolo.text #prendi titolo
        dati_articoli[nome][articolo]["URL"] = url.get_attribute("href") #prendi URL

        if (len(articoli[i].find_elements(By.CLASS_NAME, "entry__author")) > 0):
            dati_articoli[nome][articolo]["autore"] = articoli[i].find_element(By.CLASS_NAME, "entry__author").text #prendi autore, se esiste
        dati_articoli[nome][articolo]["data"] = articoli[i].find_element(By.CLASS_NAME, "entry__date").text #prendi testo
        if(len(articoli[i].find_elements(By.CLASS_NAME, "entry__summary")) > 0):
            dati_articoli[nome][articolo]["riassunto"] = articoli[i].find_element(By.CLASS_NAME, "entry__summary").text #prendi summary, se esiste
        write_to_json(dati_articoli, JSON_URL) #salva dati su json

    return

def scrape_ilGiornale(url:str, nome:str, prompt:list, driver):
    driver.get(url) #vai alla pagina
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))).click() #clicca su cookie
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "action-btn-search"))).click() #clicca su bottone search

    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-form__input"))) #clicca su search bar
    search.click()
    search.clear()

    for i in prompt:
        search.send_keys(i)
        search.send_keys(" ")

    search.send_keys(Keys.RETURN)
    # clicca, ripulisci input, aggiungi keyword e invia

    t.sleep(2)
    dati_articoli: dict = defaultdict(dict)  # inizializza diz vuoto

    for i in range(NUM_OF_ENTRIES):
        try:
            blocco = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div/div[3]/div")))
        except:
            if i == 0:
               print("Nessun articolo trovato con questo input")
            return

        articoli = blocco.find_elements(By.XPATH, "./*")

        articolo = "articolo " + str(i + 1)  # crea stringa di ID articolo

        dati_articoli[nome][articolo] = defaultdict(dict) #inizializza dizionario innestato vuoto

        titolo = articoli[i].find_element(By.CLASS_NAME, "card__title")
        dati_articoli[nome][articolo]["titolo"] = titolo.text
        dati_articoli[nome][articolo]["URL"] = titolo.get_attribute("href")
        dati_articoli[nome][articolo]["data"] = articoli[i].find_element(By.CLASS_NAME, "card__time").text
        dati_articoli[nome][articolo]["autore"] = articoli[i].find_element(By.CLASS_NAME, "card__authors").text
        dati_articoli[nome][articolo]["riassunto"] = articoli[i].find_element(By.CLASS_NAME, "card__abstract").text
        write_to_json(dati_articoli, JSON_URL)  # salva dati su json

    return

def scrape_ilFatto(url:str, nome:str, prompt:list, driver):
    driver.get(url)  # vai alla pagina
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cl-consent"]/div[1]/div[1]/div[4]/a[3]'))).click() #clicca su cookie
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ifq-header__utils-menu-main-toggle'))).click() #clicca su cookie

    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ifq-main-menu__search-input"))) #clicca su search bar
    search.click()
    search.clear()

    for i in prompt:
        search.send_keys(i)
        search.send_keys(" ")

    search.send_keys(Keys.RETURN)
    # clicca, ripulisci input, aggiungi keyword e invia

    dati_articoli: dict = defaultdict(dict)  # inizializza diz vuoto

    for i in range(NUM_OF_ENTRIES):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ifq-news-category--two-items')))
        except:
            if i == 0:
               print("Nessun articolo trovato con questo input")
            return

        articoli = driver.find_elements(By.CLASS_NAME, "ifq-news-category--two-items")

        if (i >= len(articoli)):
            return

        articolo = "articolo " + str(i + 1)  # crea stringa di ID articolo

        dati_articoli[nome][articolo] = defaultdict(dict)  # inizializza dizionario innestato vuoto

        titolo = articoli[i].find_element(By.CLASS_NAME, "ifq-news-category__title")
        url = titolo.find_element(By.XPATH, "./*")

        dati_articoli[nome][articolo]["titolo"] = titolo.text  # prendi titolo
        dati_articoli[nome][articolo]["URL"] = url.get_attribute("href")  # prendi URL
        dati_articoli[nome][articolo]["autore"] = articoli[i].find_element(By.CLASS_NAME, "ifq-news-meta__author-name").text # prendi autore
        dati_articoli[nome][articolo]["data"] = articoli[i].find_element(By.CLASS_NAME, "ifq-news-category__datetime").text # prendi data

        write_to_json(dati_articoli, JSON_URL)  # salva dati su json

    return

def scrape_Stampa(url:str, nome:str, prompt:list, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'iubenda-cs-accept-btn'))).click() #clicca su cookie
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div[6]/div[2]/div/div[1]/button[2]'))).click() #clicca su cookie

    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div[5]/div/div/div[2]/div/form/div/input[1]')))  # clicca su search bar
    search.click()
    search.clear()

    for i in prompt:
        search.send_keys(i)
        search.send_keys(" ")

    search.send_keys(Keys.RETURN)
    # clicca, ripulisci input, aggiungi keyword e invia

    dati_articoli: dict = defaultdict(dict)

    for i in range(NUM_OF_ENTRIES):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'block__item')))
        except:
            if i == 0:
               print("Nessun articolo trovato con questo input")
            return
        blocco = driver.find_element(By.CLASS_NAME, 'block__grid')
        articoli = blocco.find_elements(By.CLASS_NAME, "block__item")

        if (i >= len(articoli)):
            return

        articolo = "articolo " + str(i + 1)  # crea stringa di ID articolo

        dati_articoli[nome][articolo] = defaultdict(dict)  # inizializza dizionario innestato vuoto

        titolo = articoli[i].find_element(By.CLASS_NAME, "entry__title")
        url = titolo.find_element(By.XPATH, "./*")

        dati_articoli[nome][articolo]["titolo"] = titolo.text  # prendi titolo
        dati_articoli[nome][articolo]["URL"] = url.get_attribute("href")  # prendi URL

        if(len(articoli[i].find_elements(By.CLASS_NAME, "entry__author")) > 0):
            dati_articoli[nome][articolo]["autore"] = articoli[i].find_element(By.CLASS_NAME,"entry__author").text  # prendi autore

        write_to_json(dati_articoli, JSON_URL)  # salva dati su json
    return

def scrape_Messaggero(url:str, nome:str, prompt:list, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'iubenda-cs-btn-primary'))).click() #clicca su cookie
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="msg-search-btn"]'))).click() #clicca su search

    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="msg-menu__content"]/div[2]/form/input[3]')))  # clicca su search bar
    search.click()
    search.clear()

    for i in prompt:
        search.send_keys(i)
        search.send_keys(" ")

    search.send_keys(Keys.RETURN)
    # clicca, ripulisci input, aggiungi keyword e invia

    dati_articoli: dict = defaultdict(dict)

    for i in range(NUM_OF_ENTRIES):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".col-xs-6.html_base_bottom")))
        except:
            if i == 0:
               print("Nessun articolo trovato con questo input")
            return
        articoli = driver.find_elements(By.CSS_SELECTOR, ".col-xs-6.html_base_bottom")

        if(i >= len(articoli)):
            return

        articolo = "articolo " + str(i + 1)  # crea stringa di ID articolo

        dati_articoli[nome][articolo] = defaultdict(dict)  # inizializza dizionario innestato vuoto

        titolo = articoli[i].find_element(By.CSS_SELECTOR, '.item_content [href]')

        dati_articoli[nome][articolo]["titolo"] = titolo.get_attribute("title")  # prendi titolo
        dati_articoli[nome][articolo]["URL"] = titolo.get_attribute("href")  # prendi URL

        dati_articoli[nome][articolo]["data"] = articoli[i].find_element(By.CLASS_NAME,"data-pubblicazione-search").text  # prendi data

        write_to_json(dati_articoli, JSON_URL)  # salva dati su json
    return

user_input = input("Cosa vuoi cercare? ") #leggi input dell'utente
split_prompt = user_input.split() #splitta in diverse stringhe
driver = webdriver.Chrome(options=options) #inizializza driver con opzioni definite
scrapers = [scrape_repubblica, scrape_ilGiornale, scrape_ilFatto, scrape_Stampa, scrape_Messaggero]

start_time = t.time()
for i in range(len(LIST_OF_SITES)):
    print(f"Checking {SITE_NAMES[i]}...")
    scrapers[i](url=LIST_OF_SITES[i], nome=SITE_NAMES[i], prompt=split_prompt, driver=driver)
    finish_time = t.time()
    print(f"Completato in {round(finish_time - start_time, 2)} secondi.")
    start_time = finish_time

