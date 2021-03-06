
import json
import falcon

from util.log import AppLogger


logger = AppLogger.get_logger(__name__)

class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        logger.info('process response')

        if 'result' not in req.context:
            return

        api_reply = { 'status': 'success',
                      'links' : [],
                      'result': req.context['result'] }
        resp.body = json.dumps(api_reply, indent=2)

        logger.info('response sent')
        logger.debug('response sent: ' + resp.body)
