import json
import time


class EventDb():
    def __init__(self):
        self.event_log_handle = None
        self.ids = {}
        self.pubkeys = {}
        self.metadata = {}
        self.counter = 0
        self.tests = 0
        self.dups = 0
        self.oldest = int(time.time()) + 1000000
        self.newest = 0
        self.relays = {}
        self.kinds = {}

    def visit(self, dct, value):
        if value not in dct:
            dct[value] = 0
        dct[value] += 1
        return dct[value]

    def log_event(self, event_str):
        if not self.event_log_handle:
            self.event_log_handle = open("events.jsonl", "a")
        self.event_log_handle.write("{}\n".format(event_str))

    def process(self, event):
        self.log_event(json.dumps(event))

        self.counter += 1
        if event["id"] in self.ids:
            self.dups += 1
        if event["content"] == "test":
            self.tests += 1
        self.visit(self.pubkeys, event["pubkey"])
        self.visit(self.ids, event["id"])
        self.visit(self.kinds, event["kind"])
        if event["created_at"] < self.oldest:
            self.oldest = event["created_at"]
        if event["created_at"] > self.newest:
            self.newest = event["created_at"]
        for tag in event["tags"]:
            if len(tag) > 2 and (tag[0] == 'e' or tag[0] == 'p'):
                self.visit(self.relays, tag[2])
        if event["kind"] == 0:  # set_metadata
            self.metadata[event["pubkey"]] = json.loads(event["content"])
        if event["kind"] == 2:  # recommend_server
            self.visit(self.relays, event["content"])

    def dict(self):
        return {
            "relays": len(self.relays),
            "kinds": len(self.kinds),
            "metadata": len(self.metadata),
            "messages": self.counter,
            "dups": self.dups,
            "tests": self.tests,
            "ids": len(self.ids),
            "pubkeys": len(self.pubkeys),
            "oldest": self.oldest,
            "newest": self.newest
        }

    def json(self):
        return json.dumps(self.dict())
