import logging
import unittest
from unittest.mock import MagicMock, patch

from pydht import IncomingConnectionHandler

logging.disable(logging.CRITICAL)


class TestIncomingConnectionHandler(unittest.TestCase):

    def setUp(self):
        self.connection_handler = IncomingConnectionHandler()

    def test_sets_transport(self):
        self.connection_handler.connection_made('TRANSPORT')

        self.assertEqual(self.connection_handler.transport, 'TRANSPORT')

    @patch('pydht.incoming_connection_handler.decode', new=MagicMock(return_value={'q': 'some_query'}))
    def test_calls_attached_callback(self):
        """
        Tests that if the instance of `IncomingConnectionHandler` has an
        attached query handler, it is called
        """

        query_handler_mock = MagicMock()
        setattr(self.connection_handler, 'handle_some_query', query_handler_mock)

        self.connection_handler.datagram_received(b'some payload', ('localhost', 5000))

        query_handler_mock.assert_called_once_with({'q': 'some_query'}, ('localhost', 5000))

    @patch('pydht.incoming_connection_handler.decode', new=MagicMock(return_value={'q': 'some_query'}))
    def test_callback_does_not_exist(self):
        """
        Callback for the query does not exist and the method does not throw an exception
        """

        self.connection_handler.datagram_received(b'some payload', ('localhost', 5000))

    @patch('pydht.incoming_connection_handler.decode', new=MagicMock(return_value=10))
    def test_decoded_value_not_dictionary(self):
        """
        Handles cases where the function cannot extract the query
        """

        self.connection_handler.datagram_received(b'some payload', ('localhost', 5000))

    @patch('pydht.incoming_connection_handler.decode', side_effect=ValueError)
    def test_decode_failed(self, decode_mock):
        self.connection_handler.datagram_received(b'some payload', ('localhost', 5000))

    @patch('pydht.incoming_connection_handler.encode')
    def test_sends_response(self, encode_mock):
        encode_mock.return_value = b'some payload'

        transport_mock = MagicMock()
        self.connection_handler.transport = transport_mock

        self.connection_handler.respond({'message': 'payload'}, ('localhost', 5000))

        encode_mock.assert_called_once_with({'message': 'payload'})
        self.connection_handler.transport.sendto.assert_called_once_with(b'some payload', ('localhost', 5000))

