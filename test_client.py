import json
import sys
import time
import uuid
import websocket
import _thread
from event import Event
from common import NostrNode, relays
from eventdb import EventDb


class Client(NostrNode):
    def __init__(self):
        self.relays = {}
        self.subscriptions = {}
        self.running = True
        self.eventdb = EventDb()
        _thread.start_new_thread(self.reader, ())

    def close(self):
        self.running = False
        for i in self.relays:
            self.relays[i].close()

    def add_relay(self, url):
        self.relays[url] = websocket.create_connection(url)
        return self

    def send(self, payload):
        payload_str = json.dumps(payload)
        for relay in self.relays:
            print("sending payload: {}".format(payload_str))
            self.relays[relay].send(payload_str)
        return self

    def send_content_from_user(self, pubkey, content):
        event = Event(pubkey, Event.KIND_TEXT_NOTE, content).dict()
        self.send(["EVENT", event])
        return self

    def process_message(self, message_str):
        message = json.loads(message_str)
        message_processing_map = {
            "OK": self.process_message_default,
            "EOSE": self.process_message_default,
            "NOTICE": self.process_message_default,
            "EVENT": self.process_message_event
        }
        if message[0] not in message_processing_map:
            self.error("unknown message type: {}".format(message[0]))
        else:
            proc_func = message_processing_map[message[0]]
            return proc_func(message)
        return self

    def process_message_event(self, message):
        event = message[2]
        if event["kind"] in [0, 2, 3, 4, 7, 20000, 70202] or len(event["content"]) > 300:
            pass
        else:
            print("EVENT: {}, {}: {}".format(event["pubkey"], event["kind"], event["content"].replace("\n", " ")))
        self.eventdb.process(event)
        return self

    def process_message_default(self, message):
        print("message: {}".format(message))
        return self

    def check_relays(self, subscription_id):
        for relay in self.relays:
            counter = 0
            while counter < 110:  # TODO
                result = self.relays[relay].recv()
                self.process_message(result)
                counter += 1
        return self

    def subscribe(self):
        filter_dict = {
            # "authors": [FAKE_MAPPING["vasil9v"]],
            "limit": 100 # TODO
        }
        subscription_id = uuid.uuid4().hex
        print("subscription_id: " + subscription_id)
        self.send(["REQ", subscription_id, filter_dict])
        self.subscriptions[subscription_id] = subscription_id
        return self

    def unsubscribe(self, subscription_id):
        for relay in self.relays:
            self.send(["CLOSE", subscription_id])
            del self.subscriptions[subscription_id]
        return self

    def unsubscribe_all(self):
        for i in list(self.subscriptions.keys()):
            self.unsubscribe(i)

    def reader(self):
        while self.running:
            for i in list(self.subscriptions.keys()):
                self.check_relays(i)
            time.sleep(1.0)
        self.unsubscribe_all()
        print("exiting reader thread")

    def cli(self, config):
        while self.running:
            command = input("> ")
            if command == "exit" or command == "x":
                self.close()
            if command == "subscribe" or command == "s":
                self.subscribe()
            if command == "unsubscribe" or command == "u":
                self.unsubscribe_all()
            if command == "stats":
                print(self.eventdb.json())
                print(self.eventdb.relays)
                print(self.eventdb.kinds)
            if command == "send":
                config["pubkey"] = config.get("pubkey", input("pubkey> "))
                config["privkey"] = config.get("privkey", input("privkey> "))
                Event.PRIV_KEY = config["privkey"]
                message = input("message> ")
                if len(message) > 0:
                    self.send_content_from_user(config["pubkey"], message)


if __name__ == "__main__":
    config = {}
    if len(sys.argv) > 1:
        config = json.loads(sys.argv[1])
    client = Client()
    client.add_relay(relays[0]).cli(config)
