# python manage.py runserver

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

def index(request):
    return render(request, 'myapp/index.html')

def about(request):
    return render(request, 'myapp/about.html')

def services(request):
    return render(request, 'myapp/services.html')

def service_result(request):
    return render(request, 'myapp/service_result.html')

def service_no_result(request):
    return render(request, 'myapp/service_no_result.html')

@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        try:
            result = my_python_function(data)  # Appel à une fonction Python
            return JsonResponse({'result': result, 'success': True})
        except IndexError:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

########
def process_data(request):
    if request.method == 'POST':
        data = request.POST.get('data', '')
        image_paths = my_python_function(data)
        relative_image_paths = [os.path.relpath(path, 'myapp/static') for path in image_paths]
        return JsonResponse({'image_paths': relative_image_paths})
    return render(request, 'myapp/index.html')
########


    
##### OUTIL DE PREVISION ####
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import regex as re
import requests
import shutil

# Import dataset
data_set_reco = pd.read_csv("C:/Users/lohof/Desktop/Datadream/Wcs_data/projet_2/data_set_reco.csv", sep=",")
data_set_prevision = pd.read_csv("C:/Users/lohof/Desktop/Datadream/Wcs_data/projet_2/data_set_prevision.csv", sep = ",")

# Correction traitement des dates
data_set_reco["release_date"] = pd.to_datetime(data_set_reco["release_date"])
data_set_reco["release_date"] = data_set_reco["release_date"].dt.year
data_set_prevision["release_date"] = pd.to_datetime(data_set_prevision["release_date"])
data_set_prevision["release_date"] = data_set_prevision["release_date"].dt.year

# Définition de X
X = data_set_reco.loc[:,"Aventure":]
X_bis = data_set_reco.loc[:, ["release_date", "runtime", "averageRating"]]
X = pd.concat([X, X_bis], axis=1)

# Définition des colonnes_params (du data_set de prévision)
colonnes_params = data_set_prevision.loc[:,"Aventure":]
colonnes_params_bis = data_set_prevision.loc[:, ["release_date", "runtime", "averageRating"]]
colonnes_params = pd.concat([colonnes_params, colonnes_params_bis], axis=1)

# Entrainement du modèle
from sklearn.neighbors import NearestNeighbors
modelnn = NearestNeighbors(n_neighbors=6).fit(X)

# Création colonne titre nettoyé
data_set_prevision["clean_title"]=data_set_prevision["original_title"]
data_set_prevision["clean_title"]=data_set_prevision["clean_title"].str.lower().str.strip()
data_set_prevision["clean_title"]=data_set_prevision["clean_title"].apply(lambda x : re.sub(r"\s",r"", x))
data_set_prevision["clean_title"]=data_set_prevision["clean_title"].apply(lambda x : re.sub(r"'",r"", x))
accents = ["à","â","ä","é","è","ê","ë","î","ï","ô","ö","ù","û", "ü", "ÿ", "ç"]
sans_accents = ["a", "a", "a", "e","e","e","e","i","i","o","o","u","u","u","y","c"]
for lettre in range(len(accents)):
    data_set_prevision["clean_title"]=data_set_prevision["clean_title"].apply(lambda x : x.replace(accents[lettre], sans_accents[lettre]) if (accents[lettre] in x) else x)

def my_python_function(film):
    result = []
    result_nom = []
    film = str(film)
    
    # Nettoyage input
    film = film.lower().strip()
    film = re.sub(r"\s",r"", film)
    film = re.sub(r"'",r"", film)
    accents = ["à","â","ä","é","è","ê","ë","î","ï","ô","ö","ù","û", "ü", "ÿ", "ç"]
    sans_accents = ["a", "a", "a", "e","e","e","e","i","i","o","o","u","u","u","y","c"]
    for lettre in range(len(accents)):
        film=film.replace(accents[lettre], sans_accents[lettre]) if (accents[lettre] in film) else film

    # Prévision/ gestion erreurs
    try :
        imdb_film = data_set_prevision.imdb_id[data_set_prevision["clean_title"]==film]
        imdb_film = list(imdb_film)[0]
        prevision = modelnn.kneighbors(data_set_prevision.loc[data_set_prevision["imdb_id"] == imdb_film, colonnes_params.columns])
    except IndexError:
        raise IndexError("Film not found in the dataset")
    except Exception as e:
        raise Exception(f"Unexpected error : {str(e)}")
    
    film_prevu = data_set_prevision.loc[data_set_prevision['imdb_id'] == imdb_film, "original_title"]
    
    # Si film déjà dans liste des reco : on passe le premier voisin (element +1)
    # Si film pas déjà dans liste des reco : on garde le premier voisin (element)
    verif_doublon = data_set_reco.iloc[prevision[1][0][0], 6]
    verif_doublon = verif_doublon.lower().strip()
    verif_doublon = re.sub(r"\s",r"", verif_doublon)
    verif_doublon = re.sub(r"'",r"", verif_doublon)
    accents = ["à","â","ä","é","è","ê","ë","î","ï","ô","ö","ù","û", "ü", "ÿ", "ç"]
    sans_accents = ["a", "a", "a", "e","e","e","e","i","i","o","o","u","u","u","y","c"]
    for lettre in range(len(accents)):
        verif_doublon=verif_doublon.replace(accents[lettre], sans_accents[lettre]) if (accents[lettre] in verif_doublon) else verif_doublon
   
    # Génère les nouvelles mages
# Écrire les nouvelles images
    for element in range(5):
        if verif_doublon == film:
            result = "https://image.tmdb.org/t/p/original/" + data_set_reco.iloc[prevision[1][0][element+1], 9]
            response = requests.get(result)
            with open(f"C:/Users/lohof/Desktop/Datadream/Wcs_data/projet_2/site/kungfupandas/myproject/myapp/static/myapp/images/test{element}.jpg", "wb") as f:
                f.write(response.content)
            result_nom.append(data_set_reco.iloc[prevision[1][0][element+1], 6])
        else:
            result = "https://image.tmdb.org/t/p/original/" + data_set_reco.iloc[prevision[1][0][element], 9]
            response = requests.get(result)
            with open(f"C:/Users/lohof/Desktop/Datadream/Wcs_data/projet_2/site/kungfupandas/myproject/myapp/static/myapp/images/test{element}.jpg", "wb") as f:
                f.write(response.content)
            result_nom.append(data_set_reco.iloc[prevision[1][0][element], 6])


    return # f"{result_nom[0]}\n{result_nom[1]}\n{result_nom[2]}\n{result_nom[3]}\n{result_nom[4]}"
