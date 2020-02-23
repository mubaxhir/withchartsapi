import configparser
from flask import jsonify
from mongoengine import connect
from models.datasets_model import Dataset_mongo
from models.decks_model import Deck_dataset_item,Deck_chart_item,Deck_mongo
from models.charts_model import Chart_mongo


# Parsing of definitions from the configuration file

config = configparser.ConfigParser()
#config.read('C:/Dev/Python/withchartsapi_v0.2.0-requirements/api/config.ini')
config.read('/home/mubashir/withchartsapi_v0.2.0-requirements/api/config.ini')

# Connnection to the MongoDB database

connect(db=config['MONGODB_CONFIG']['DB_NAME'], host = str(config['MONGODB_CONFIG']['DB_HOST']))


# Definition of a function for the POST verb of the /decks endpoint

def post_deck(body):

    new_deck = Deck_mongo(
        deck_name = body['deck_name'],
        deck_datasets=[],
        deck_charts=[]
        )

    new_deck.save()
    return jsonify({"deck_id":str(new_deck.pk)})



# Definition of a function for the GET verb of the /decks endpoint

def get_decks():
    """Retrieve all Decks

    This retrieves all existing *Decks*. The GET request returns a list of *Deck objects*.

    :rtype: Decks
    """
    return [deck.condensed() for deck in Deck_mongo.objects]


# Definition of a function for the GET verb of the /decks/{deck_id} endpoint

def get_deck_by_id(deck_id, extended=None):

    try:
        deck = Deck_mongo.objects.get(pk=deck_id)
        if (extended==True):
            return deck.ext()
        else:
            return deck.condensed()

    except:
        return jsonify(error = 'Resource not found',status = 404,message = 'Deck with requested deck_id not found')


# Definition of a function for the PATCH verb of the /decks/{deck_id} endpoint

def patch_deck_by_id(deck_id, op, path, value=None):

     # spliting the dataset ID or chart ID from path in list
     # e.g: "/deck_dataset/8f65fg65fg65f6f" = ["","deck_dataset","8f65fg65fg65f6f"]

    path = path.split('/')

    try:

        # checks for all 4 operations

        if(op == "add" and path[-1] == 'deck_datasets' and value != None):
            datasets = list(Deck_mongo.objects.get(pk=deck_id).deck_datasets)
            print(datasets)
            datasets.append({"dataset_id":str(value)})
            updated_deck = Deck_mongo.objects(pk=deck_id).update(set__deck_datasets = datasets)
            updated_deck.save()
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.condensed()

        elif (op == "replace" and path[-1] == 'deck_name' and value != None):
            Deck_mongo.objects(pk=deck_id).update(set__deck_name = value)
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.condensed()

        elif (op=="remove" and path[-2] == "deck_datasets" and value == None):
            datasets = list(Deck_mongo.objects.get(pk=deck_id).deck_datasets)
            for dataset in datasets:
                if(str(dataset.dataset_id.pk) == path[-1]):
                    datasets.remove(dataset)
            deck = Deck_mongo.objects(pk=deck_id)
            if deck:
                deck = deck.get(pk=deck_id)
                deck.update(set__deck_datasets = datasets)
                deck.save()
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.condensed()

        elif (op=="remove" and path[-2] == "deck_charts" and value == None):
            charts = list(Deck_mongo.objects.get(pk=deck_id).deck_charts)
            for chart in charts:
                if(str(chart.chart_id.pk) == path[-1]):
                    charts.remove(chart)
            deck = Deck_mongo.objects(pk=deck_id)
            if deck:
                deck = deck.get(pk=deck_id)
                deck.update(set__deck_charts = charts)
                deck.save()
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.condensed()

        # if checks are not true then 400 Bad Request 

        else:
            return jsonify(error = 'Bad request', status = 400, message = 'Request not allowed')

    # if deck ID not found then

    except:
        return jsonify(error = 'Resource not found', status = 404, message = 'Deck with requested deck_id not found')
