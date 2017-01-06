
from marshmallow_sqlalchemy import ModelSchema

import models

class ExampleSchema(ModelSchema):
    class Meta:
        model = models.Example


