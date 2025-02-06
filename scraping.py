#_______________________________________________________________________________
#Import des packages

import requests
import bs4
import pandas as pd
from datetime import datetime, date, timedelta
import schedule
import time
import os


#_______________________________________________________________________________
#VDéfinition des chemins

wd_csv="data_flunet.csv"


#_______________________________________________________________________________
#Formatage des données

def formater(df):
    #Formater le pays
    i=0
    j=0
    old_countries=["Lao People's Democratic Republic", "Netherlands (Kingdom of the)", "Syrian Arab Republic", "Venezuela (Bolivarian Republic of)", "Iran (Islamic Republic of)", "United Kingdom, Scotland", "China, Hong Kong SAR", "Kosovo (in accordance with UN Security Council resolution 1244 (1999))", "United Republic of Tanzania", "United Kingdom, Northern Ireland", "Bolivia (Plurinational State of)", "Saint Martin (French part)", "Republic of Moldova", "Democratic People's Republic of Korea", "occupied Palestinian territory, including east Jerusalem", "Russian Federation", "Serbia and Montenegro (2003-2006)", "United Kingdom, England", "United Kingdom, Wales", "French Guiana", "Guadeloupe", "Republic of Korea", "Saint Barthélemy", "New Caledonia", "Martinique"]
    new_countries=["Laos", "Netherlands", "Syria", "Venezuela", "Iran", "Scotland", "Hong Kong", "Kosovo", "Tanzania", "Northern Ireland", "Bolivia", "France", "Moldova", "South Korea", "Palestine", "Russia", "Serbia", "England", "Wales", "France", "France", "South Korea", "France", "France", "France"]
    while j < len(df.COUNTRY_AREA_TERRITORY):
        while i < len(old_countries) :
            if df.COUNTRY_AREA_TERRITORY[j] == old_countries[i]:
                df.loc[[j], ["COUNTRY_AREA_TERRITORY"]] = new_countries[i]
                break
            i+=1
        i=0
        j+=1
    return df


#_______________________________________________________________________________
#Scrapping des données + mise sous .csv

def auto_parser():
    url="https://www.who.int/tools/flunet"
    r=requests.get(url)
    auto_soup=bs4.BeautifulSoup(r.text, "html.parser")
    auto_data=auto_soup.find("div", id="PageContent_C018_Col00")
    auto_lien=auto_data.find("div", class_="sf-content-block content-block").find("a").get("href")
    response = requests.get(auto_lien, stream=True)
    temp_file = "data_flunet.csv"
    with open(temp_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    df = pd.read_csv(temp_file)
    return df


#_______________________________________________________________________________
#Récupérer les nouvelles données (on trie par date, et on prend celles qui sont supérieures à la dernière date)

def new_data (df):
    #Dernière date de notre csv
    last_date=pd.read_csv(wd_csv).sort_values(by="ISO_WEEKSTARTDATE", ascending=False).ISO_WEEKSTARTDATE[0]
    count=0
    sorted_df=df.sort_values(by="ISO_WEEKSTARTDATE", ascending=False)
    #On compte le nombre d'enregistrements sup à last_date
    for row in sorted_df.ISO_WEEKSTARTDATE:
        if row > last_date:
            count+=1
        else :
            break
    filtered_df=sorted_df[:count]
    return filtered_df


#_______________________________________________________________________________
#Ajouter les nouvelles valeurs à notre csv

def add_values(filtered_df):
    filtered_df.to_csv(wd_csv, mode="a", header=False)

def once():
    df=auto_parser()
    df2=formater(df)
    df2.to_csv(wd_csv)
    print(date.today(), " : Data Updated")

once()


#_______________________________________________________________________________
#Automatisation du web-scrapping

def auto():
    filtered_df=formater(new_data(auto_parser()))
    add_values(filtered_df)
    print(date.today(), " : Data Updated")


#schedule.every().monday.at("10:00").do(auto)

while True :
    schedule.run_pending()
    time.sleep(1)



