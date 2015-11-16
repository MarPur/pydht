import datetime

BUCKET_SIZE = 8

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

    def _truncate_id(self, node_id, length):
        return (int.from_bytes(node_id, 'big') >> (160 - length) << (160 - length))

    def _add_node(self, node_id, information, update_timestamp=True):

        for (prefix, prefix_length), nodes in self._prefix_to_bucket.items():
            # bits which are longer than the prefix, are set to 0 in node_id
            # if the first prefix_length bits of the node_id match prefix, and the bucket
            # is not full, then we add the node to the bucket.
            # If the node_id falls in a bucket which is full and covers our id,
            # we split the bucket and add the new node

            truncated_node_id = self._truncate_id(node_id, prefix_length)

            if truncated_node_id ^ prefix == 0:

                if len(nodes) < self._bucket_size:
                    info = information.copy()
                    info['id'] = node_id

                    if update_timestamp:
                        info['last_contacted'] = _current_time()

                    nodes.append(info)

                    return True
                else:
                    our_truncated_id = self._truncate_id(self._our_id, prefix_length)

                    # the node we are trying to add is our close neighbour who we care about
                    # therefore we split bucket by removing the bucket,
                    # creating two new prefixes with 0 and 1 as additional bits we check for at the end
                    # of the prefix, and adding back the removed nodes
                    if our_truncated_id ^ prefix == 0:
                        nodes_to_readd = nodes

                        del self._prefix_to_bucket[(prefix, prefix_length)]

                        self._prefix_to_bucket[(prefix, prefix_length + 1)] = []
                        self._prefix_to_bucket[(prefix | (1 << (160 - prefix_length - 1)), prefix_length + 1)] = []

                        # we are not contacting these nodese, so we do not want to update the timestamp
                        # of when we last contacted them
                        for node in nodes_to_readd:
                            self._add_node(node['id'], node, update_timestamp=False)

                        # this is a new node we just learnt about, therefore, we have to update its timestamp
                        self._add_node(node_id, information, update_timestamp=True)

                        return True

        return False

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

        return self._add_node(node_id, information, update_timestamp=True)

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
        :return: True if the node was removed from the routing table, False otherwise
        :rtype: bool
        """

        was_removed = False

        for (prefix, prefix_length), nodes in self._prefix_to_bucket.items():
            truncated_node_id = self._truncate_id(node_id, prefix_length)

            if truncated_node_id ^ prefix == 0:

                self._prefix_to_bucket[(prefix, prefix_length)] = list(filter(
                    lambda node: node['id'] != node_id,
                    nodes
                ))

                was_removed = was_removed or len(self._prefix_to_bucket[(prefix, prefix_length)]) != len(nodes)

        return was_removed


    def get_node(self, node_id):
        """
        Gets information of a given node

        :param node_id: Node's ID
        :type node_id: bytes
        :return: dictionary that was stored when node was created if the node is found. None otherwise
        :rtype: dict
        """
        for (prefix, prefix_length), nodes in self._prefix_to_bucket.items():
            truncated_node_id = self._truncate_id(node_id, prefix_length)

            if truncated_node_id ^ prefix == 0:

                nodes_found = list(filter(
                    lambda node: node['id'] == node_id,
                    nodes
                ))

                if len(nodes_found) > 0:
                    return nodes_found[0]

        return None
