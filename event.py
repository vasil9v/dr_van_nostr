import json
import secp256k1
import time
from hashlib import sha256

class Event:
    PRIV_KEY = None  # FIXME
    KIND_META = 0
    KIND_TEXT_NOTE = 1
    KIND_RELAY_REC = 2

    def __init__(self, pubkey, kind, content, tags=[]):
        self.id = None
        self.sig = None
        self.privkey = Event.PRIV_KEY
        self.pubkey = pubkey
        self.kind = kind
        self.content = content
        self.tags = tags
        self.created_at = self.get_unix_timestamp()

    def get_hash(self):
        serialized_event = [
          0,
          self.pubkey,
          self.created_at,
          self.kind,
          self.tags,
          self.content
        ]
        serialized_event_string = json.dumps(serialized_event, separators=(',', ':'))
        return sha256(serialized_event_string.encode('utf-8')).hexdigest()

    def get_id(self):
        return self.get_hash()

    def get_sig(self):
        """
        from: https://github.com/monty888/nostrpy/blob/master/nostr/event/event.py#L257
        """
        self.id = self.get_id()

        # pk = secp256k1.PrivateKey(priv_key)
        pk = secp256k1.PrivateKey()
        pk.deserialize(self.privkey)

        # sig = pk.ecdsa_sign(self._id.encode('utf-8'))
        # sig_hex = pk.ecdsa_serialize(sig).hex()
        id_bytes = (bytes(bytearray.fromhex(self.id)))
        sig = pk.schnorr_sign(id_bytes, bip340tag='', raw=True)
        return sig.hex()

    def get_unix_timestamp(self):
        return int(time.time())

    def finalize(self):
        assert(self.privkey is not None), "error: private key needs to be set"
        self.id = self.get_id()
        self.sig = self.get_sig()
        return self

    def dict(self):
        self.finalize()
        return {
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.sig
        }

    def json(self):
        return json.dumps(self.dict())

    @staticmethod
    def event_from_json(event_json):
        return Event.event_from_dict(json.loads(event_json))

    @staticmethod
    def event_from_dict(event_dict):
        event = Event(event_dict["pubkey"], event_dict["kind"], event_dict["content"], event_dict["tags"])
        event.id = event_dict["id"]
        event.sig = event_dict["sig"]
        event.created_at = event_dict["created_at"]
        return event
