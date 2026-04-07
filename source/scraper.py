import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
import os
from datetime import datetime


# URL base i punt d'entrada del scraper
BASE_URL = "https://www.pisos.com"
URL_ENTRADA = "https://www.pisos.com/alquiler/pisos-barcelona_capital/"

# capçaleres HTTP per simular un navegador real
# (apartat 6.1 dels apunts: Modificació del user agent)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control": "no-cache",
    "dnt": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}

# Delay fix entre peticions en segons
# (apartat 6.4 dels apunts: Espaiat de peticions HTTP)
delay_segons = 2


def descarregar_pagina(url):
    """
    Descarrega el contingut HTML d'una URL donada.

    Args:
        url (str): URL a descarregar

    Returns:
        BeautifulSoup: objecte amb el contingut parsejat, o None si hi ha error
    """
    try:
        # creem la request fent servir els headers definits abans i
        # un timeout de 10 segons per si el servidor no respongués
        resposta = requests.get(url, headers=headers, timeout=10)
        return BeautifulSoup(resposta.content, "html.parser")

    except requests.exceptions.RequestException:
        pass


def extreure_links_anuncis(soup):
    """
    extreu els links de tots els anuncis d'una pàgina de llistat.
    implementa el descobriment autònom d'enllaços

    Args:
        soup: contingut parsejat de la pàgina de llistat

    Returns:
        list: llista de urls absolutes dels anuncis trobats
    """
    links = []

    # busquem tots els divs amb classe "ad-preview" que contenen els anuncis
    # estructura identificada havent inspeccionat l'HTML de pisos.com
    anuncis = soup.find_all("div", class_="ad-preview")

    for anunci in anuncis:
        # obtenim el link de cada anunci des de l'atribut data-lnk-href
        link = anunci.get("data-lnk-href")
        if link:
            # Construïm la URL absoluta afegint la base
            url_completa = BASE_URL + link
            links.append(url_completa)

    return links


def extreure_link_seguent_pagina(soup):
    """
    Extreu el link de la pàgina seguent per implementar la paginacio autonoma.

    Args:
        soup: contingut parsejat de la pàgina actual

    Returns:
        str: url de la pàgina seguent, o None si és l'última pàgina
    """
    # busquem el link de la següent pàgina
    # amb la inspecció html vam veure que el botó de pàgina següent esta dins del div "pagination__next"
    seguent_div = soup.find("div", class_="pagination__next")
    if seguent_div:
        seguent = seguent_div.find("a")
        if seguent:
            return BASE_URL + seguent.get("href")
    return None



def extreure_caracteristica(soup, label):
    """
    Funcio per extreure el valor d'una caracteristica concreta
    de la fitxa d'un pis, buscant per l'etiqueta.

    Args:
        soup: contingut parsejat de la fitxa
        label: nom de la característica a buscar

    Returns:
        str: valor de la caracteristica, o buit si no es troba
    """
    # busquem tots els labels de caracteristiques, amb la info de la inspecció previa
    labels = soup.find_all("span", class_="features__label")

    for l in labels:
        if label in l.get_text():
            # com que els dos spans som germans fem servir el find_next_sibling
            valor = l.find_next_sibling("span", class_="features__value")
            if valor:
                # afegim el strio=True per eliminar impureses
                return valor.get_text(strip=True)

    return ""


def extreure_dades_anunci(url):
    """
    Accedeix a la fitxa individual d'un anunci i n'extreu totes les dades.

    Args:
        url: url de la fitxa de l'anunci

    Returns:
        list: llista amb les dades del pis en ordre
    """
    soup = descarregar_pagina(url)
    if not soup:
        return None

    # trobem el títol en el h1 corresponent
    titol_tag = soup.find("h1", class_="detail-info__title")
    # afegim un if per en cas de que no ho trobi no peti
    titol = titol_tag.get_text(strip=True) if titol_tag else ""

    # trobem el preu a l'atribut data-ad-price del div principal
    contenidor = soup.find("div", attrs={"data-ad-price": True})
    preu = contenidor.get("data-ad-price") if contenidor else ""

    # fem el mateix amb la ubicació
    ubicacio_tag = soup.find("p", class_="detail-info__subtitle")
    ubicacio = ubicacio_tag.get_text(strip=True) if ubicacio_tag else ""

    # fent servir la funció que hem creat abans extrec les característiques lligades al seu tag
    # ja que tenen totes la mateixa classe
    sup_construida = extreure_caracteristica(soup, "Superficie construida")
    sup_util = extreure_caracteristica(soup, "Superficie util")
    habitacions = extreure_caracteristica(soup, "Habitaciones")
    banys = extreure_caracteristica(soup, "Banos")
    planta = extreure_caracteristica(soup, "Planta")
    referencia = extreure_caracteristica(soup, "Referencia")

    # definim també la data d'extracció per si en un futur volem veure l'evolució
    data_extraccio = datetime.now().strftime("%Y-%m-%d")

    # retornem una llista amb els valors en ordre
    return [
        url,
        titol,
        preu,
        ubicacio,
        sup_construida,
        sup_util,
        habitacions,
        banys,
        planta,
        referencia,
        data_extraccio
    ]


def guardar_csv(dades, fitxer_sortida):
    """
    Guarda la llista de dades en un fitxer CSV.

    Args:
        dades: llista de llistes amb les dades dels pisos
        fitxer_sortida: nom del fitxer CSV de sortida
    """

    # noms de les columnes del csv
    capcalera = [
        "url",
        "titol",
        "preu_eur",
        "ubicacio",
        "superficie_construida_m2",
        "superficie_util_m2",
        "habitacions",
        "banys",
        "planta",
        "referencia",
        "data_extraccio"
    ]

    # guardem el csv amb el csv.writer de forma molt similar als apunts
    with open(fitxer_sortida, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(capcalera)
        for fila in dades:
            writer.writerow(fila)
    #finalment afegeixo informació per saber si ha funcionat o no
    print(f"\nDataset guardat a: {fitxer_sortida}")
    print(f"Total de pisos extrets: {len(dades)}")


def main(max_pagines, fitxer_sortida):
    """
    Funcio principal que coordina tot el proces de scraping. Mentre
    debuggem i així podem veure on es falla

    Args:
        max_pagines: nombre maxim de pàgines a processar
        fitxer_sortida: nom del fitxer CSV de sortida
    """
    # creo la llista buida per emmagatzemar les dades
    totes_les_dades = []
    url_pagina_actual = URL_ENTRADA
    pagina_num = 1

    # bucle principal sota la condició de que la url no sigui none i sigui menor al màxim definit de pàgines
    while url_pagina_actual and pagina_num <= max_pagines:
        # ensenyem per pantalla per quina pagina va el bucle
        print(f"\n pagina {pagina_num}")

        # descarreguem la pàgina
        soup_llistat = descarregar_pagina(url_pagina_actual)
        if not soup_llistat:
            print(" error -- no s'ha pogut descarregar la pagina")
            break

        # extraiem els links dels anuncis
        links_anuncis = extreure_links_anuncis(soup_llistat)
        if not links_anuncis:
            print("error - No s'han trobat anuncis")
            break

        # bucle dels anuncis
        for url_anunci in links_anuncis:
            # afegim info per saber quin anunci estem processant cada moment
            print(f"  processant: {url_anunci}")

            # delay entre peticions per no saturar el servidor
            time.sleep(delay_segons)

            # extraiem les dades de la fitxa individual
            dades = extreure_dades_anunci(url_anunci)
            if dades:
                totes_les_dades.append(dades)

        # extraiem el link de la pàgina següent
        url_pagina_actual = extreure_link_seguent_pagina(soup_llistat)
        pagina_num += 1

    # guardem totes les dades en CSV
    guardar_csv(totes_les_dades, fitxer_sortida)


# mitjançant un parser definim els arguments del script
# el número de pàgines a scrapear i si volem canviar el nom del output csv
parser = argparse.ArgumentParser(
    description="Scraper de pisos en lloguer a Barcelona - pisos.com"
)
parser.add_argument(
    "--max_pagines",
    type=int,
    default=3,
    help="Nombre maxim de pagines a processar (default: 3)"
)
parser.add_argument(
    "--output",
    type=str,
    default="../dataset/pisos_barcelona.csv",
    help="Nom del fitxer CSV de sortida (default: dataset/pisos_barcelona.csv)"
)

args = parser.parse_args()

# Creem la carpeta de sortida si no existeix
os.makedirs(os.path.dirname(args.output), exist_ok=True)

# Executem el scraper
main(args.max_pagines, args.output)