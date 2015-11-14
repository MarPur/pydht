from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

from pydht.routing_table import RoutingTable, BUCKET_SIZE


class TestAddNote(unittest.TestCase):
    """
    Test Suite to check if the Routing Table correctly inserts a node
    to the routing table
    """

    def setUp(self):
        self.routing_table = RoutingTable(b'\xff' * 40)

        self.datetime_patch = patch('pydht.routing_table._current_time', new=MagicMock(return_value=datetime(2015, 1, 7, 21, 15, 0)))
        self.datetime_patch.start()

    def tearDown(self):
        self.datetime_patch.stop()

    def test_add_node_first_level_zero_bucket(self):
        """
        Inserting a node with id 000...0 into the routing table. It should go
        to the 0 bucket
        """
        # 000...0
        new_node_id = (0).to_bytes(20, 'big')
        result = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertTrue(result)

        # Bucket 1 is empty
        self.assertEqual(len(self.routing_table._prefix_to_bucket[(1 << 159, 1)]), 0)

        # Bucket 0 has the added node
        self.assertEqual(len(self.routing_table._prefix_to_bucket[(0, 1)]), 1)

        node = self.routing_table._prefix_to_bucket[(0, 1)][0]
        self.assertDictEqual(node, {
            'id': new_node_id,
            'key1': 'value1',
            'key2': 'value2',
            'last_contacted': datetime(2015, 1, 7, 21, 15, 0)
        })

    def test_add_node_first_level_one_bucket(self):
        """
        Inserting a node with id 100...0 into the routing table. It should go
        to the 1 bucket
        """
        new_node_id = (0 | 1 << 159).to_bytes(20, 'big')

        result = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertTrue(result)

        # Bucket 0 is empty
        self.assertEqual(len(self.routing_table._prefix_to_bucket[(0, 1)]), 0)

        # Bucket 1 has the added node
        self.assertEqual(len(self.routing_table._prefix_to_bucket[(1 << 159, 1)]), 1)

        node = self.routing_table._prefix_to_bucket[(1 << 159, 1)][0]
        self.assertDictEqual(node, {
            'id': new_node_id,
            'key1': 'value1',
            'key2': 'value2',
            'last_contacted': datetime(2015, 1, 7, 21, 15, 0)
        })

    def test_not_add_node_full_bucket(self):
        """
        The node cannot be inserted into the routing table, because the bucket,
        the node belongs to, is full.
        """

        new_node_id = (0).to_bytes(20, 'big')
        self.routing_table._prefix_to_bucket[(0, 1)] = [{}] * self.routing_table._bucket_size

        result = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertFalse(result)

        self.assertListEqual(self.routing_table._prefix_to_bucket[(1 << 159, 1)], [])
        self.assertListEqual(self.routing_table._prefix_to_bucket[(0, 1)], [{}] * BUCKET_SIZE)

