# tipologia-pract1
Repositori de la Practica 1 de Tipologia de les dades

# Autors 
- Alexander Morales Fajarnés
- Esteve Creus

# Dataset: 
El dataset resultant es el detall dels pisos en alquiler a Barcelona
DOI de Zenodo del dataset generat: https://zenodo.org/records/19461707

Aquest repositori conté el dataset generat a partir de dades de la pàgina web pisos.com.

## Estructura

- /dataset → Ubicació del dataset generat en format CSV
- /source → Ubicació del script Python de scraping
- /dataset/pisos_barcelona.csv → Dataset generat pel codi de python en format CSV
- /source/scraper.py → Codi python que descarrega el dataset
- requirements.txt → Fitxer amb les llibreries de python necesàries per executar el codi.

## Reproducció del dataset

Executar:

python scraper.py

## Variables
- --max_pagines → Numero de pàgines a descarregar.
- --output → Nom del fitxer.

## Llibreries utilitzades

Veure requirements.txt