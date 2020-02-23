from mongoengine import StringField,ReferenceField,DictField,Document
from models.datasets_model import Dataset_mongo
from flask import jsonify

# Charts model for API v0.2.0
#
# A MongoDB **chart** document's schema is represented by the **Chart_mongo** class with the following fields:
# - chart_title: the title of the Chart
# - chart_metric: the metric of the Chart (Y-axis)
# - chart_attribute: the attribute of the Chart (X-axis)
# - dataset_id: the dataset from which values are queried.

# Definition of the Chart_mongo class

class Chart_mongo(Document):
    chart_title = StringField(required=True)
    chart_metric = StringField(required=True)
    chart_attribute = StringField(required=True)
    dataset_id = ReferenceField(Dataset_mongo)
    chart_data = DictField()
    meta = {'collection': 'Charts'}

    def to_json(self):
        return dict({
            "chart_id": str(self.pk),
            "chart_title":str(self.chart_title),
            "chart_metric":str(self.chart_metric),
            "chart_attribute":str(self.chart_attribute),
            "dataset_id": str(self.dataset_id.pk),
            "chart_data": dict(self.chart_data)
        })
