import configparser
from flask import jsonify
from mongoengine import connect
from models.charts_model import Chart_mongo
import inflect
from pattern.en import pluralize, singularize
from models.datasets_model import Dataset_mongo,Datacontent_mongo
from models.decks_model import Deck_dataset_item,Deck_chart_item,Deck_mongo

p = inflect.engine()

# Parsing of definitions from the configuration file

config = configparser.ConfigParser()
#config.read('C:/Dev/Python/withchartsapi_v0.2.0-requirements/api/config.ini')
config.read('/home/mubashir/withchartsapi_v0.2.0-requirements/api/config.ini')

# Connnection to the MongoDB database

connect(db=config['MONGODB_CONFIG']['DB_NAME'], host = str(config['MONGODB_CONFIG']['DB_HOST']))


# Definition of a function for the POST verb of the /charts endpoint

def post_chart(body):
    
    try:        
        if p.singular_noun(body["chart_metric"]) is False: 
            title = pluralize(body["chart_metric"]) + " by " + singularize(body["chart_attribute"])
        else:
            title = body["chart_metric"] + " by " + singularize(body["chart_attribute"])

        datacontent = Dataset_mongo.objects.get(pk=body["dataset_id"]).datacontent_id
        
        pipeline = [
            {  '$unwind': "$datacontent_values" },
            { '$group' : 
                { '_id' : { body["chart_attribute"] : '$datacontent_values.'+body["chart_attribute"]}, 
                body["chart_metric"] : { '$sum' : '$datacontent_values.'+body["chart_metric"] }
                }
            }
        ]
        
        data_cursor = Datacontent_mongo.objects(pk=datacontent.pk).aggregate(*pipeline)
        data = {x["_id"][str(body["chart_attribute"])] :x[str(body["chart_metric"])] for x in data_cursor}

        new_chart = Chart_mongo(
            chart_title=str(title),
            dataset_id=body["dataset_id"], 
            chart_metric=body["chart_metric"], 
            chart_attribute=body["chart_attribute"],
            chart_data=data
            )
        new_chart.save()

        Deck_mongo.objects(pk=body["deck_id"]).update(push__deck_charts=Deck_chart_item(chart_id=new_chart.pk))

        return new_chart.to_json()
    except:
            return jsonify(error = 'Bad request', status = 400, message = 'Request not allowed')


# Definition of a function for the GET verb of the /charts/{chart_id} endpoint

def get_chart_by_id(chart_id):

    try:

        result = Chart_mongo.objects.get(pk=chart_id)
        return {"chart":result.to_json()}

    except:
        return jsonify(error = 'Resource not found', status = 404, message = 'chart with requested chart_id not found')
