import json
import sys
import websocket
from event import Event


class NostrNode:
    def __init__(self):
        pass

    def error(self, message):
        print(message)


class Client(NostrNode):
    def __init__(self):
        self.relays = {}

    def close(self):
        for i in self.relays:
            self.relays.close()

    def add_relay(self, url):
        self.relays[url] = websocket.create_connection(url)
        return self

    def send(self, payload):
        payload_str = json.dumps(payload)
        for relay in self.relays:
            print("payload: {}".format(payload_str))
            self.relays[relay].send(payload_str)
            result = self.relays[relay].recv()
            print("result: " + result)
        return self

    def send_content_from_user(self, pubkey, content):
        event = Event(pubkey, Event.KIND_TEXT_NOTE, content).dict()
        self.send(["EVENT", event])
        return self


relays = [
    "wss://nostr-pub.wellorder.net",
    "wss://nostr-relay.wlvs.space",  # returns informative errors
    "wss://nostr-verified.wellorder.net",
    "wss://nostr.openchain.fr",
    "wss://relay.damus.io",
    "wss://relay.nostr.info",
    "wss://nostr.oxtr.dev",
    "wss://nostr.semisol.dev",
    "wss://nostr-relay.untethr.me",
    "wss://nostr.bitcoiner.social",
    "wss://nostr.onsats.org",
    "wss://nostr.drss.io",
    "wss://nostr.rocks",
    "wss://nostr.rdfriedl.com",
    "wss://nostr-pub.semisol.dev",
    "wss://nostr.ono.re",
    "wss://nostr.nodeofsven.com/",
]

config = json.loads(sys.argv[1])
Event.PRIV_KEY = config["privkey"]

client = Client()
client.add_relay(relays[1]).send_content_from_user(config["pubkey"], "test 9")
