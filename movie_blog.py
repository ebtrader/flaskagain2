from flask import Flask, render_template
import urllib.request, json
from pathlib import Path

import os

# https://www.themoviedb.org/documentation/api/discover

application = Flask(__name__)

raw_path = r'C:\Users\Owner\OneDrive\Documents\Python'

formatted_path = raw_path.replace("\\", "/")

filepath = Path(formatted_path)

username_path = filepath / 'tmdb.txt'

with open(username_path) as h:
    username = h.read()

TMDB_API_KEY = username

# https://api.themoviedb.org/3/discover/movie?api_key=5974f64cb93effab2377fd923ec5475c
@application.route("/")
def get_movies():
    url = "https://api.themoviedb.org/3/discover/movie?api_key={}".format(TMDB_API_KEY)

    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return render_template ("movies.html", movies=dict["results"])


@application.route("/movies")
def get_movies_list():
    url = "https://api.themoviedb.org/3/discover/movie?api_key={}".format(TMDB_API_KEY)

    response = urllib.request.urlopen(url)
    movies = response.read()
    dict = json.loads(movies)

    movies = []

    for movie in dict["results"]:
        movie = {
            "title": movie["title"],
            "overview": movie["overview"],
        }

        movies.append(movie)

    return {"results": movies}

@application.route("/popular")
def get_popular():
    url = "https://api.themoviedb.org/3/discover/movie?sort_by=popularity.descapi_key={}".format(TMDB_API_KEY)

    response = urllib.request.urlopen(url)
    movies = response.read()
    dict = json.loads(movies)

    movies = []

    for movie in dict["results"]:
        movie = {
            "title": movie["title"],
            "overview": movie["overview"],
        }

        movies.append(movie)

    return {"results": movies}



if __name__ == '__main__':
    application.run()