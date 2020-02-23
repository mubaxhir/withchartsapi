import os
import configparser
from uuid import uuid4
from flask import jsonify
from mongoengine import connect
from werkzeug.utils import secure_filename
from core.basic_algorithm import Dataset_core
from models.datasets_model import Dataset_mongo,Datacontent_mongo


# Parsing of definitions from the configuration file

config = configparser.ConfigParser()
#config.read('C:/Dev/Python/withchartsapi_v0.2.0-requirements/api/config.ini')
config.read('/home/mubashir/withchartsapi_v0.2.0-requirements/api/config.ini')

# Connnection to the MongoDB database

connect(db=config['MONGODB_CONFIG']['DB_NAME'], host = str(config['MONGODB_CONFIG']['DB_HOST']))


# Definition of a function for the POST verb of the /datasets endpoint

def post_dataset_with_file(source_file):

    # Generation of source_filename (secure name) and stored_filename (UUID4)

    source_filename, file_ext = os.path.splitext(source_file.filename)
    source_filename = secure_filename(source_filename+file_ext)
    generated_name = uuid4()
    stored_filename = str(str(generated_name) + file_ext)

    # Storage of file in storage folder

    file_path = str(config['FILESTORAGE_CONFIG']['STORAGE_FOLDER'])+stored_filename

    while os.path.exists(file_path):

        file_path = str(config['FILESTORAGE_CONFIG']['STORAGE_FOLDER'])+"%s%s" % (str(generated_name), file_ext)
        generated_name = uuid4()

    source_file.save(file_path)

    # Check of the file extension against allowed extensions and check of file size against the maximum file size

    if (file_ext in config.get('FILESTORAGE_CONFIG', 'ALLOWED_EXTENSION').split(',') and os.stat(file_path).st_size <= int(config['FILESTORAGE_CONFIG']['MAX_FILE_SIZE'])):

        # If checks are succesful
        # Generation of the dataset with the Dataset_core class of the core algorithm

        generated_dataset = Dataset_core(file_path)

        # Definition and saving of the MongoDB Dataset document

        dataset_document = Dataset_mongo(
            dataset_columns=generated_dataset.columns,
            dataset_rows=generated_dataset.rows,
            source_filename=source_filename,
            stored_filename=generated_dataset.filename,
            dataset_headers=generated_dataset.headers)

        dataset_document.save()

        # Generation of the datacontent with the Dataset_core class of the core algorithm

        generated_dataset.generate_content()

        # Definition and saving of the MongoDB Datacontent document

        datacontent_document = Datacontent_mongo(
            dataset_id=dataset_document,
            datacontent_values = generated_dataset.values)

        datacontent_document.save(validate=False)

        # Insertion of the reference to the Datacontent document into the Dataset document

        dataset_document.datacontent_id = datacontent_document

        dataset_document.save()

        # Return of the Dataset's id

        return jsonify({"dataset_id":str(dataset_document.id)})

    # Operations if checks are not succesful

    else:

        # Removal of the stored file from the storage folder

        os.remove(file_path)

        # Return of the 400 response

        return jsonify(error = 'File not supported', status = 400, message = 'Provided source_file not supported (extension or size)')


# Definition of a function for the GET verb of the /datasets endpoint

def get_datasets():

    #retrieves all datasets in array and retruns

    return [x.to_dict() for x in Dataset_mongo.objects()]


# Definition of a function for the GET verb of the /datasets/{dataset_id} endpoint

def get_dataset_by_id(dataset_id):

    try:

        result = Dataset_mongo.objects.get(pk=dataset_id)
        return jsonify(result.to_dict())

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the GET verb of the /datasets/{dataset_id}/datacontent endpoint

def get_datacontent_for_dataset_id(dataset_id):

    # try:
        #retrieves the datacontent by dataset_id in dataset

    datacontent = Dataset_mongo.objects.get(pk=dataset_id).datacontent_id

    #retrieves the datacontent by datacontent_id

    response = Datacontent_mongo.objects.get(pk=datacontent.pk)

    return response.to_json()

    # except:
    #     return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')
