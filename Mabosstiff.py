import json
import http
from lib.BanDog import BanDog
import logging

logging.basicConfig(
    filename="log/Mabosstiff.log", encoding="utf-8", level=logging.INFO
)
# http.client.HTTPConnection.debuglevel = 1

config = json.loads(open("config.json", "r").read())
auto_resolver = BanDog(don_url=config["DonURL"], access_token=config["AccessToken"])
auto_resolver.watch_public_stream()
