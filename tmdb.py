#let's import all the packages we need
#requests: package used to query API and get the result back in Python
#json: package used to read and convert JSON format
#csv: package used to read and write csv

import requests,json,csv,os
from pathlib import Path

# https://towardsdatascience.com/this-tutorial-will-make-your-api-data-pull-so-much-easier-9ab4c35f9af

#document all the parameters as variables
raw_path = r'C:\Users\Owner\OneDrive\Documents\Python'

formatted_path = raw_path.replace("\\", "/")

filepath = Path(formatted_path)

username_path = filepath / 'tmdb.txt'

with open(username_path) as h:
    username = h.read()

API_key = username

Movie_ID = '464052'

#write a function to compose the query using the parameters provided
def get_data(API_key, Movie_ID):
    query = 'https://api.themoviedb.org/3/movie/'+Movie_ID+'?api_key='+API_key+'&language=en-US'
    response = requests.get(query)
    if response.status_code==200:
    #status code ==200 indicates the API query was successful
        array = response.json()
        text = json.dumps(array)
        return (text)
    else:
        return ("error")

def write_file(filename, text):
    dataset = json.loads(text)
    csvFile = open(filename,'a')
    csvwriter = csv.writer(csvFile)
    #unpack the result to access the "collection name" element
    try:
        collection_name = dataset['belongs_to_collection']['name']
    except:
        #for movies that don't belong to a collection, assign null
        collection_name = None
    result = [dataset['original_title'],collection_name]
    # write data
    csvwriter.writerow(result)
    print(result)
    csvFile.close()

movie_list = ['464052','508442']
#write header to the file
csvFile = open('movie_collection_data.csv','a')
csvwriter = csv.writer(csvFile)
csvwriter.writerow(['Movie_name','Collection_name'])
csvFile.close()
for movie in movie_list:
    text = get_data(API_key, movie)
    #make sure your process breaks when the pull was not successful
    #it's easier to debug this way
    if text == "error":
        break
    write_file('movie_collection_data.csv', text)