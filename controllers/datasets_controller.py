# import connexion
from flask import jsonify
from mongoengine import connect
from core.basic_algorithm import Dataset_core
from models.datasets_model import Dataset_mongo

connect(host="mongodb+srv://mubi:1234@cluster001-avto2.mongodb.net/test?retryWrites=true&w=majority")

def post_dataset_with_file(source_file):  # noqa: E501
    dataPath = "/home/mubashir/deep_learning_with_python/withchartsapi_v0.1.1/storage/"+str(source_file.filename)
    source_file.save(dataPath)
    data = Dataset_core(dataPath)
    mongodata = Dataset_mongo(dataset_columns=data.columns,dataset_rows=data.rows,dataset_filename=data.filename,dataset_headers=data.headers)
    # dataSet = Dataset_mongo.objects.get(dataset_filename=data.filename)
    # if dataSet:
    #     return jsonify({"dataset_id":str(dataSet["id"]})
    # else:
    mongodata.save()
    dataSet=Dataset_mongo.objects.get(dataset_filename=data.filename)
    print(dataSet["id"])
    return jsonify({"dataset_id":str(dataSet["id"])})

def get_dataset_by_id(requested_dataset_id):  # noqa: E501
    result=Dataset_mongo.objects.get(pk=requested_dataset_id)
    return result.to_json()
