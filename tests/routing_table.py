from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

from pydht.routing_table import RoutingTable, BUCKET_SIZE

to_bytes = lambda x: x.to_bytes(20, 'big')


class TestAddNote(unittest.TestCase):
    """
    Test Suite to check if the Routing Table correctly inserts a node
    to the routing table
    """

    def setUp(self):
        self.routing_table = RoutingTable(b'\xff' * 20)

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
        new_node_id = to_bytes(0)
        was_added = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertTrue(was_added)

        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [{
                'id': new_node_id,
                'key1': 'value1',
                'key2': 'value2',
                'last_contacted': datetime(2015, 1, 7, 21, 15, 0)
            }],
            (1 << 159, 1): []
        })

    def test_add_node_first_level_one_bucket(self):
        """
        Inserting a node with id 100...0 into the routing table. It should go
        to the 1 bucket
        """
        new_node_id = to_bytes(1 << 159)

        was_added = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertTrue(was_added)

        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [],
            (1 << 159, 1): [{
                'id': new_node_id,
                'key1': 'value1',
                'key2': 'value2',
                'last_contacted': datetime(2015, 1, 7, 21, 15, 0)
            }]
        })

    def test_not_add_node_full_bucket(self):
        """
        The node cannot be inserted into the routing table, because the bucket,
        the node belongs to, is full.
        """

        new_node_id = to_bytes(0)
        self.routing_table._prefix_to_bucket[(0, 1)] = [{'id': to_bytes(i)} for i in range(10, 10 + self.routing_table._bucket_size)]

        was_added = self.routing_table.add_node(new_node_id, {'key1': 'value1', 'key2': 'value2'})

        self.assertFalse(was_added)

        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [{'id': to_bytes(i)} for i in range(10, 10 + self.routing_table._bucket_size)],
            (1 << 159, 1): []
        })

    def test_split_bucket(self):
        """
        Tests that the bucket is split correctly, when the bucket is full and
        the bucket's prefix covers our ID
        """

        self.routing_table = RoutingTable(b'\xff' * 20, bucket_size=2)

        self.routing_table._prefix_to_bucket[(1 << 159, 1)] = [
            # node_id: 101000...0
            {'key1': 'node1', 'last_contacted': 1, 'id': to_bytes(5 << 157)},
            # node_id: 11000...0
            {'key2': 'node2', 'last_contacted': 1, 'id': to_bytes(6 << 157)}
        ]

        # 111000...0
        new_node_id = to_bytes(7 << 157)
        
        was_added = self.routing_table.add_node(new_node_id, {'key': 'value'})
        
        self.assertTrue(was_added)
        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [],
            (1 << 159, 2): [
                {'key1': 'node1', 'last_contacted': 1, 'id': to_bytes(5 << 157)}
            ],
            (3 << 158, 2): [
                {'key2': 'node2', 'last_contacted': 1, 'id': to_bytes(6 << 157)},
                {'key': 'value', 'last_contacted': datetime(2015, 1, 7, 21, 15, 0), 'id': new_node_id}
            ]
        })


class TestRemoveNode(unittest.TestCase):

    def setUp(self):
        self.routing_table = RoutingTable(to_bytes(0))

    def test_removes_existing_node(self):
        """
        Removes node which exists in the routing table
        """

        node_id = to_bytes(0)
        self.routing_table._prefix_to_bucket[(0, 1)] = [
            {'id': node_id},
            {'id': to_bytes(255)}
        ]

        was_removed = self.routing_table.remove_node(node_id)

        self.assertTrue(was_removed)

        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [
                {'id': to_bytes(255)}
            ],
            (1 << 159, 1): []
        })

    def test_remove_non_existing_node(self):
        """
        Tries to remove a node which does not exist in the routing table
        """

        self.routing_table._prefix_to_bucket[(0, 1)] = [
            {'id': to_bytes(255)}
        ]

        was_removed = self.routing_table.remove_node(to_bytes(0))

        self.assertFalse(was_removed)

        self.assertDictEqual(self.routing_table._prefix_to_bucket, {
            (0, 1): [
                {'id': to_bytes(255)}
            ],
            (1 << 159, 1): []
        })


class TestGetNode(unittest.TestCase):

    def setUp(self):
        self.routing_table = RoutingTable(to_bytes(0))

    def test_gets_existing_node(self):
        self.routing_table._prefix_to_bucket[(0, 1)] = [
            {'id': to_bytes(0), 'key1': 'val1', 'key2': 'val2'}
        ]

        node = self.routing_table.get_node(to_bytes(0))

        self.assertDictEqual(node, {
            'id': to_bytes(0),
            'key1': 'val1',
            'key2': 'val2'
        })

    def test_tries_to_retrieve_non_existing_node(self):
        self.routing_table._prefix_to_bucket[(0, 1)] = [
            {'id': to_bytes(255), 'key1': 'val1', 'key2': 'val2'}
        ]

        node = self.routing_table.get_node(to_bytes(0))

        self.assertIsNone(node)
