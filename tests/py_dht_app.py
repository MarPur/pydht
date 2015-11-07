import logging
import unittest
from unittest.mock import MagicMock, patch

from pydht import PyDhtApp, IncomingConnectionHandler

logging.disable(logging.CRITICAL)

class TestPyDhtApp(unittest.TestCase):

    def setUp(self):
        self.app = PyDhtApp()
        self.app.incoming_connection_handler = MagicMock(spec=IncomingConnectionHandler)
        self.app.client_id = 'CLIENT_ID'

    def test_handle_ping(self):
        request = {
            't': 'transaction'
        }

        self.app.handle_ping(request, ('localhost', 5000))

        expected_response = {
            't': 'transaction',
            'y': 'r',
            'r': {
                'id': 'CLIENT_ID'
            }
        }
        self.app.incoming_connection_handler.respond.assert_called_once_with(expected_response, ('localhost', 5000))

    def test_handles_malformed_request(self):
        request = None

        self.app.handle_ping(request, ('localhost', 5000))
        self.assertFalse(self.app.incoming_connection_handler.respond.called)