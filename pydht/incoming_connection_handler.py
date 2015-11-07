from asyncio import DatagramProtocol
import logging

from bencode import encode, decode


class IncomingConnectionHandler(DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        logging.info('Connection made')

    def datagram_received(self, payload, addr):
        logging.info('Received datagram %s', payload)

        try:
            request = decode(payload)

            logging.info('Received request %s', request)

            query = request.get('q')

            callback = getattr(self, 'handle_' + query)
        except (ValueError, AttributeError):
            logging.warning('Could not handle the request')
        else:
            callback(request, addr)

    def respond(self, response, addr):
        payload = encode(response)
        self.transport.sendto(payload, addr)