import asyncio
import hashlib
import logging
import uuid

from .incoming_connection_handler import IncomingConnectionHandler
from .routing_table import RoutingTable


class PyDhtApp:

    def __init__(self):
        generated_id = uuid.uuid1()

        self.client_id = hashlib.sha1(generated_id.bytes).digest()
        self.incoming_connection_handler = None
        self.routing_table = RoutingTable(self.client_id)

    @asyncio.coroutine
    def start(self, loop):
        _, self.incoming_connection_handler = yield from loop.create_datagram_endpoint(
            IncomingConnectionHandler, local_addr=('localhost', 6881)
        )

        self.incoming_connection_handler.handle_ping = self.handle_ping
        self.incoming_connection_handler.handle_find_node = self.handle_find_node()

    def handle_ping(self, request, sender):
        logging.info('Handling ping from %s', sender)

        try:
            transaction_id = request.get('t')
            requestor_id = request.get('a').get('id')
        except AttributeError:
            logging.warning('Malformed request. Could not retrieve the required values')
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

            self.routing_table.add_node(requestor_id, {'source': sender})

    def handle_find_node(self, request, sender):
        logging.info('Handling find_peer from %s', sender)

        try:
            transaction_id = request.get('t')
            requestor_id = request.get('a').get('id')
            target_id = request.get('a').get('target')
        except AttributeError:
            logging.warning('Malformed request. Could not retrieve the required values')
        else:
            closest_neighbours = self.routing_table.get_closest_nodes(requestor_id)

            response = {
                't': transaction_id,
                'y': 'r',
                'r': {
                    'id': self.client_id,
                    'nodes': ''
                }
            }

            logging.info('Sending response %s', response)

            self.incoming_connection_handler.respond(response, sender)

            self.routing_table.add_node(requestor_id, {'source': sender})