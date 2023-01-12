# dr_van_nostr
simple library for nostr

## Install

```
pip install websocket-client
pip install secp256k1
```

## Run

```
python test_client.py '{"pubkey": "<your public key>", "privkey": "<your private key>"}'
```
You can make a public and private key pair at [nostr.com](nostr.com) or anywhere else really. The private key is used to sign the `sig` field of events which are matched against the `id` and `pubkey` fields by the relay.
[Here](https://github.com/nostr-protocol/nostr) is more information on the protocol.

After you run the above, you should be able to retrieve it from the relay you sent it to. But this client currently does not poll for messages. I currently verify it was sent by finding the event in [https://nostr.info/relays/](https://nostr.info/relays/).
