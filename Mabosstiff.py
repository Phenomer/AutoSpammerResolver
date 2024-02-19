import json
import http
from lib.BanDog import BanDog

# http.client.HTTPConnection.debuglevel = 1

config = json.loads(open("config.json", "r").read())
auto_resolver = BanDog(don_url=config["DonURL"], access_token=config["AccessToken"])
auto_resolver.watch_public_stream()
