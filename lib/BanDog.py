#!/usr/bin/env python3

import json
from urllib.parse import urlparse
from websockets.sync.client import connect
from datetime import datetime
from .SpammerResolver import SpammerResolver


class BanDog(SpammerResolver):
    def is_spam(self, payload):
        if (
            len(payload["account"]["username"]) == 10
            and urlparse(payload["account"]["avatar"]).path
            == "/avatars/original/missing.png"
            and len(payload["mentions"]) >= 2
            and self.after_x_day(payload["account"]["created_at"])
        ):
            return True
        return False

    def time_str(self):
        return datetime.now().strftime("%y%m%d_%H%M%S_%f")

    def save_blacklist(self, payload):
        with open(f"log/blacklist/{self.time_str()}.json", "a") as log_file:
            log_file.write(json.dumps(payload, indent=4, ensure_ascii=False))

    def save_whitelist(self, payload):
        with open(f"log/whitelist/{self.time_str()}.json", "a") as log_file:
            log_file.write(json.dumps(payload, indent=4, ensure_ascii=False))

    def spam_check(self, payload):
        if not self.is_spam(payload):
            # self.save_whitelist(payload)
            return

        self.save_blacklist(payload)
        account_info = {
            "id": payload["account"]["id"],
            "username": payload["account"]["username"],
            "display_name": payload["account"]["display_name"],
            "acct": payload["account"]["acct"],
            "note": payload["account"]["note"],
            "avatar": payload["account"]["avatar"],
            "header": payload["account"]["header"],
            "created_at": payload["account"]["created_at"],
        }
        self.logger.info(json.dumps(account_info, indent=4, ensure_ascii=False))
        self.logger.info(json.dumps(payload["mentions"], indent=4, ensure_ascii=False))
        self.logger.info(payload["content"])

        # スパムレポートを提出
        report = self.write_spam_report(
            account_id=account_info["id"], status_id=payload["id"]
        )
        # 速攻suspendする
        self.suspend(target_id=account_info["id"], report_id=report["id"])

    def watch_public_stream(self):
        don_host = urlparse(self.don_url).netloc
        with connect(
            f"wss://{don_host}/api/v1/streaming/?stream=public:remote",
            additional_headers=self.authentication_header(),
        ) as ws:
            self.logger.info("connected.")
            while True:
                data = json.loads(ws.recv())
                if data["event"] != "update":
                    continue
                payload = json.loads(data["payload"])
                self.spam_check(payload=payload)
