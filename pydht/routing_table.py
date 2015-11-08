BUCKET_SIZE = 8


class RoutingTable:

    def __init__(self, our_id, bucket_size=BUCKET_SIZE):
        """
        :param our_id: Our ID
        :type our_id: bytes
        :param bucket_size: Size of each bucket
        :type bucket_size: int
        """
        self.bucket_size = bucket_size
        self.prefix_to_bucket = {}
        self.our_id = our_id

    def add_node(self, node_id, information):
        """
        Attempts to insert a node. If the node was successfully inserted,
        it will also add `last_contacted` value to the `information` dictionary
        with current timestamp

        :param node_id:Node's ID
        :param information: Node's information (IP, Port, etc.)
        :type node_id: bytes
        :type information: dict
        :return: True if the node was added to the bucket and False otherwise
        :rtype: bool
        """
        pass

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
