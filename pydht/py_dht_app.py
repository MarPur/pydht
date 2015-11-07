import asyncio
import hashlib
import logging
import uuid

from .incoming_connection_handler import IncomingConnectionHandler


class PyDhtApp:

    def __init__(self):
        generated_id = uuid.uuid1()

        self.client_id = hashlib.sha1(generated_id.bytes).digest()
        self.incoming_connection_handler = None

    @asyncio.coroutine
    def start(self, loop):
        _, self.incoming_connection_handler = yield from loop.create_datagram_endpoint(
            IncomingConnectionHandler, local_addr=('localhost', 6881)
        )

        self.incoming_connection_handler.handle_ping = self.handle_ping

    def handle_ping(self, request, sender):
        logging.info('Handling ping from %s', sender)

        try:
            transaction_id = request.get('t')
        except AttributeError:
            logging.warning('Malformed request. Could not get Transaction ID')
        else:
            response = {
                't': transaction_id,
                'y': 'r',
                'r': {
                    'id': self.client_id
                }
            }
            logging.info('Sending response %s', response)

            self.incoming_connection_handler.respond(response, sender)
