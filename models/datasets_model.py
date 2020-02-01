from mongoengine import StringField,IntField,ListField
from flask import jsonify
from flask_mongoengine import Document
#!/usr/bin/env python
# coding: utf-8

# Datasets model for API v0.1.1
#
# A MongoDB **dataset** document's schema is represented by the **Dataset_mongo** class with the following fields:
# - dataset_filename: the name of the Excel file including the extension
# - dataset_rows: the count of rows of the Excel file
# - dataset_columns: the count of columns of the Excel file
# - dataset_headers: the list of columns headers of the Excel file.


# Definition of the Dataset_mongo class

class Dataset_mongo(Document):
    dataset_filename = StringField(required=True)
    dataset_rows = IntField(required=True)
    dataset_columns = IntField(required=True)
    dataset_headers = ListField(StringField(), required=True)

    def to_json(self):
        return jsonify({
            "dataset_id": str(self.pk),
            "dataset_filename": self.dataset_filename,
            "dataset_rows": self.dataset_rows,
            "dataset_columns": self.dataset_columns,
            "dataset_headers": self.dataset_headers
        })
