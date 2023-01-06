from flask import Flask, render_template
import urllib.request, json
from personal_workouts_wrapper import *
import pandas as pd

import os

# https://www.themoviedb.org/documentation/api/discover

application = Flask(__name__)

# https://api.themoviedb.org/3/discover/movie?api_key=5974f64cb93effab2377fd923ec5475c
@application.route("/movies")
def get_movies_list():
    df = personal_workouts_function()
    return df.to_html(header='true', table_id='table')


if __name__ == '__main__':
    application.run()