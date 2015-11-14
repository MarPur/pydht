import datetime

BUCKET_SIZE = 8


def set_bit(value, bit):
    return value | (1 << bit)


def _current_time():
    return datetime.datetime.now()


class RoutingTable:

    def __init__(self, our_id, bucket_size=BUCKET_SIZE):
        """
        :param our_id: Our ID
        :type our_id: bytes
        :param bucket_size: Size of each bucket
        :type bucket_size: int
        """
        self._bucket_size = bucket_size

        self._prefix_to_bucket = {}
        self._prefix_to_bucket[(0, 1)] = []
        self._prefix_to_bucket[(1 << 159, 1)] = []

        self._our_id = our_id

    def add_node(self, node_id, information):
        """
        Attempts to insert a node into the routing table, so it could be retrieved later.

        :param node_id:Node's ID
        :param information: Node's information (IP, Port, etc.)
        :type node_id: bytes
        :type information: dict
        :return: True if the node was added to the bucket and False otherwise
        :rtype: bool
        """

        node_inserted = False

        for (prefix, prefix_length), nodes in self._prefix_to_bucket.items():
            # bits which are longer than the prefix, are set to 0 in node_id

            # if the first prefix_length bits of the node_id match prefix, and the bucket
            # is not full, then we add the node to the bucket

            truncated_node_id = (int.from_bytes(node_id, 'big') >> (160 - prefix_length) << (160 - prefix_length))

            if truncated_node_id ^ prefix == 0 and len(nodes) < self._bucket_size:
                info = information.copy()
                info['id'] = node_id
                info['last_contacted'] = _current_time()

                nodes.append(info)

                node_inserted = True


        return node_inserted

    def id_belongs_to_prefix(self, node_id, bucket_prefix):
        """
        Checks if the given `node_id` is covered by the `bucket_prefix`

        :param node_id: Client's ID which is checked
        :param bucket_prefix: ID Prefix of the bucket
        :type node_id: bytes
        :type bucket_prefix: bytes
        :return: True if the `bucket_prefix` covers the `node_id` and False otherwise
        :rtype: bool
        """
        pass

    def touch_node(self, node_id):
        """
        Updates node's `last_contacted` timestamp to current timestamp

        :param node_id: Node's ID
        :type node_id: bytes
        """
        pass

    def remove_node(self, node_id):
        """
        Removes node from the routing table

        :param node_id: Node's ID
        :type node_id: bytes
        """
        pass

    def get_node(self, node_id):
        """
        Gets information of a given node

        :param node_id: Node's ID
        :type node_id: bytes
        :return: dictionary that was stored when node was created
        :rtype: dict
        """
        pass
