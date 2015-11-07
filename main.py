import asyncio
import logging
import random

from pydht import PyDhtApp

dht_bootstrap_nodes = [
    ('router.utorrent.com', 6881),
    ('router.bittorrent.com', 6881)
]

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    loop = asyncio.get_event_loop()

    app = PyDhtApp()
    loop.run_until_complete(app.start(loop))

    try:
        logging.info('Starting the event loop')
        loop.run_forever()
    except KeyboardInterrupt as e:
        logging.info('Terminating the app')
    finally:
        loop.close()