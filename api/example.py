
import falcon
import sqlalchemy as sa

from json.decoder import JSONDecodeError

from middleware import AuthMiddleware, JSONTranslator, RequireJSON
from models import Example
from serializers import ExampleSchema
from util.http import max_body
from util.log import AppLogger

import settings


class ExampleResource(object):

    """
        Represents an Example element in the API.
    """
    def __init__(self, session, logger):
        self.session = session
        self.logger = logger

    def on_get(self, req, resp, example_id_in):

        example_schema = ExampleSchema()

        try:
            example_id = int(example_id_in)
        except ValueError:
            self.logger.error('Invalid example_id provided.')
            raise falcon.HTTPBadRequest(
                'Bad Request',
                'Valid ID must be provided as example/id.')
 
        try:
            if example_id:
                example = self.session.query(Example).filter(Example.id == example_id).first()
                result = example_schema.dump(example).data
            else:
                example_list = self.session.query(Example).all()
                result = [example_schema.dump(row).data for row in example_list]              
        except Exception as ex:
            self.logger.error(ex)
            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                'An error occurred processing this API call.',
                30)

        self.logger.debug('GET result data: %s' % (result, ))
        req.context['result'] = result
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(settings.MAX_BODY_SIZE))
    def on_put(self, req, resp, example_id):

        if not example_id:
            self.logger.error('PUT request: Put REQUIRES an ID to update.')
            raise falcon.HTTPBadRequest(
                'Bad Request',
                'No ID provided.')
        return self.on_post(req, resp, example_id=example_id, require_object=True)

    @falcon.before(max_body(settings.MAX_BODY_SIZE))
    def on_post(self, req, resp, example_id, require_object=False):

        example_schema = ExampleSchema(session=self.session)

        try:
            doc = req.context['doc']
            self.logger.debug('POST data: %s' % (doc, ))

            # Can't specify a doc id in the document
            self.logger.debug('example id "%s"' % (example_id, ))
            if example_id == "":
                doc['id']=""
                del(doc['id'])
            else:
                doc['id'] = example_id
            self.logger.debug('post-del %s' %(doc, ))

            instance = example_schema.get_instance(doc)
            if require_object and instance is  None:
                self.logger.error('Requires an existing object id')
                raise falcon.HTTPBadRequest(
                    'Bad Request',
                    'Example record not found with given ID or ID not provided.')

            loaded_example = example_schema.load(doc, instance=instance)
            if len(loaded_example.errors) > 0:
                self.logger.error('Deserialize example failed: %s' % (loaded_example.errors,))
                raise falcon.HTTPBadRequest(
                    'Bad Request',
                    'Valid JSON must be submitted in the request body.')
        except KeyError:
            self.logger.error('No POST document provided.')
            raise falcon.HTTPBadRequest(
                'Bad Request',
                'Valid JSON must be submitted in the request body.')
        except Exception as ex:
            self.logger.error('Exception occurred: %s' % (ex,))
            raise falcon.HTTPInternalServerError(
                'Internal Server Error',
                'An error occurred processing this request.')

        proper_example = loaded_example.data

        try:
            session.add(proper_example)
            session.commit()
        except Exception as ex:
            self.logger.error('Exception occurred during DB update: %s' % (ex,))
            raise falcon.HTTPInternalServerError(
                'Internal Server Error',
                'An error occurred processing this request.')

        resp.status = falcon.HTTP_201
        resp.location = '%s/example/%s' % (settings.API_URL, proper_example.id)
        self.logger.info('created (%s)' % (proper_example, ))

    def on_delete(self, req, resp, example_id):
        try:
            example = self.session.query(Example).filter(Example.id == example_id)
            saved_str = str(example.first())
            deleted = example.delete()
        except Exception as ex:
            self.logger.error('Exception occurred: %s' % (ex,))
            raise falcon.HTTPInternalServerError(
                'Internal Server Error',
                'An error occurred processing this request.')

        try:
            session.commit()
        except Exception as ex:
            self.logger.error('Exception occurred during DB delete: %s' % (ex,))
            raise falcon.HTTPInternalServerError(
                'Internal Server Error',
                'An error occurred processing this request.')

        resp.status = falcon.HTTP_204
        if deleted:
            req.context['result'] = '{ "message": "Deleted successfully." }'
        else:
            req.context['result'] = '{ "message": "Example entry did not exist." }'

        self.logger.info('deleted (%s)' % (saved_str, ))


logger = AppLogger.get_logger(__name__)

app = falcon.API(middleware=[
    RequireJSON(),
    JSONTranslator(),
])

engine = sa.create_engine(settings.DB_URL)
session = sa.orm.Session(engine)
Example.metadata.create_all(engine)

examples = ExampleResource(session, logger)
app.add_route('/{example_id_in}', examples)
logger.info('Endpoint is READY to process requests.')
