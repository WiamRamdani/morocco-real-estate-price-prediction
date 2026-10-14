# Les bibliothèques nécessaires
import csv
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # ou ton mot de passe XAMPP
    database="avito_db"
)

cursor = conn.cursor()

# Calcul de temps du collecte de données
start_time = time.time()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


url = "https://www.avito.ma/fr/maroc/maisons-%C3%A0_vendre?has_price=true"
driver.get(url)

# Wait for products to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Rechercher')]"))
    ) #it's optimal bc waiting stops when results appear
except Exception as e:
    print("Loading error:", e)

# Scroll the page to load more results
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

liens = []
prix = []
ville = []
type_du_bien = []
surface_tot = []
surface_habitable = []
age = []
chambres = []
salles_de_bain = []
quartier = []
terrasse = []
parking = []
sécurité = []
ascenceur = []
balcon = []
chauffage = []
climatisation = []
cuis_equipee = []
etage = []
standing = []
condition = []
salons = []
concierge = []
meuble = []
duplex = []
garage = []
jardin = []
piscine = []


soup = BeautifulSoup(driver.page_source, "html.parser")

while True:
    # 1️⃣ Scraper la page actuelle ici
    offres = soup.find_all('a', class_="sc-1jge648-0 jZXrfL")
    for offre in offres:
        data_url = offre.get("href")
        if data_url:
            # Vérifie si ce <a> est dans un div role="tabpanel"
            parent_tabpanel = offre.find_parent('div', {'role': 'tabpanel'})
            if parent_tabpanel:
                appartements = parent_tabpanel.find_all('a', class_="sc-1jge648-0 jZXrfL")
                for appart in appartements:
                    appart_url = appart.get("href")
                    if appart_url:
                        liens.append(appart_url)
            else:
                # C'est une offre normale → ajoute à la liste
                liens.append(data_url)
    
    print("🔗 Nombre de liens collectés :", len(liens))
    
    # 2️⃣ Récupérer le numéro de page actuel
    active_page_elem = driver.find_element(By.CSS_SELECTOR, ".activePage")
    active_page = active_page_elem.text
    print(f"📄 Page active : {active_page}")

    try:
        # 3️⃣ Trouver le lien `>` (dernier <a> dans le bloc pagination)
        next_button = driver.find_elements(By.CSS_SELECTOR, ".sc-2y0ggl-0 a")[-1]

        # Vérifier : est-ce que c'est bien le chevron ?
        if "ChevronRight" not in next_button.get_attribute("innerHTML"):
            print("✅ Dernière page atteinte.")
            break
        
        # Scroller jusqu'au bouton pour qu'il ne soit pas caché
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(0.5)

        # Attendre qu'il soit cliquable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(next_button)
        )

        try:
            next_button.click()
        except Exception:
            # Si toujours intercepté → utiliser JS direct
            driver.execute_script("arguments[0].click();", next_button)

        # Attendre que l'ancienne page disparaisse
        WebDriverWait(driver, 10).until(EC.staleness_of(active_page_elem))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".activePage"))
        )

        # Petite pause pour stabilité
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")

    except Exception as e:
        print("⚠️ Plus de bouton Next ou erreur :", e)
        driver.refresh()
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        continue

print("🎉 Fin de la collecte de liens !")
print(f"Nombre brut : {len(liens)}")

liens_uniques = list(set(liens))
print(f"Nombre unique : {len(liens_uniques)}")

cursor.execute("SELECT Lien FROM Avito_maison")
liens_existants = set(row[0] for row in cursor.fetchall())

    
print(f"🗂️ Liens déjà existants : {len(liens_existants)}")

liens_a_traiter = [l for l in liens_uniques if l not in liens_existants]
print(f"🚀 Liens à scraper : {len(liens_a_traiter)}")

for i, lien in enumerate(liens_a_traiter):
    try:
        driver.get(lien)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        v_prix = soup.find('p', class_=re.compile(r'sc-1x0vz2r-0.*lnEFFR'))
        prix_text = v_prix.get_text(strip=True).replace('\u202f', '').replace(' ', '') if v_prix else 'Nan'
        
        blocs = soup.find_all("div", class_="sc-19cngu6-1 doRGIC")

        infos = {}

        for bloc in blocs:
            spans = bloc.find_all("span")
            if len(spans) >= 2:
                valeur = spans[0].text
                champ = spans[1].text
                infos[champ] = valeur
            
                
        breadcrumb = soup.find("ol")
        items = breadcrumb.find_all("li")
        v_ville = items[2].get_text(strip=True) if len(items) >= 3 else 'Nan'
        v_quartier = items[3].get_text(strip=True) if len(items) >= 4 else 'Nan'
           
                
        attributes = soup.select('div.sc-19cngu6-0.dnArJl img')
        v_garage = v_jardin = v_piscine = v_balcon = v_chauffage = v_climatisation = v_parking = v_cuis_equipee = v_sécurité = v_terrasse =  v_meuble = 'Non'
        for attr in attributes:
            test = attr.get('alt', '').strip()
            if 'Terrasse' in test:
                v_terrasse = 'oui'
            elif 'Sécurité' in test:
                v_sécurité = 'oui'
            elif 'Parking' in test:
                v_parking = 'oui' 
            elif 'Balcon' in test:
                v_balcon = 'oui'
            elif 'Chauffage' in test:
                v_chauffage = 'oui'
            elif 'Climatisation' in test:
                v_climatisation = 'oui'
            elif 'Cuisine équipée' in test:
                v_cuis_equipee = 'oui'
            elif 'Meublé' in test:
                v_meuble = 'oui'
            elif 'Jardin' in test:
                v_jardin = 'oui'
            elif 'Piscine' in test:
                v_piscine = 'oui'
            elif 'Garage' in test:
                v_garage = 'oui'
            
            
        row = [
            v_ville, v_quartier, prix_text,
            infos.get('Surface totale', 'Nan'),
            infos.get('Surface habitable', 'Nan'),
            infos.get('Âge du bien', 'Nan'),
            infos.get('Chambres', 'Nan'),
            infos.get('Salle de bain', 'Nan'),
            infos.get('Salons', 'Nan'),
            infos.get('Standing', 'Nan'),
            infos.get('Condition', 'Nan'),
            infos.get('Étage', 'Nan'),
            v_terrasse, v_parking, v_sécurité,
            v_balcon, v_chauffage, 
            v_climatisation,v_cuis_equipee,
            v_meuble, v_garage, v_jardin,
            v_piscine,
            lien
        ]
       
        
        sql = """INSERT INTO Avito_maison (
            Ville, Quartier, Prix, Surface_totale, Surface_habitable,
            Age_du_bien, Chambres, Salle_de_bain, Standing, Condition,
            Etage, Terrasse, Parking, Sécurité, Balcon, Chauffage,
            Climatisation, Cuisine_équipée, Meublé, Garage, Jardin,
            Piscine, Lien
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, row)
        conn.commit()
        
        print(f"✅ [{i+1}/{len(liens_a_traiter)}] Lien traité et sauvegardé")
    
    except Exception as e:
        print(f"⚠️ Erreur sur le lien {i+1}: {lien} -> {e}")
        continue
            
cursor.close()
conn.close()            
# ✅ Fermer proprement
driver.quit()
print(f"Le temps total pour exécuter le code: {((time.time() - start_time)/60):.2f} minutes")