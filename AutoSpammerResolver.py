#!/usr/bin/python3

import requests
from requests import Response
import json
import sys

config = json.loads(open("config.json", "r").read())


class AutoSpammerResolver:
    class ProtocolError(Exception):
        pass

    def __init__(self, don_url: str, access_token: str):
        self.don_url = don_url
        self.access_token = access_token

    def response_validator(self, res: Response) -> bool:
        if res.status_code == 200:
            return True
        else:
            raise AutoSpammerResolver.ProtocolError(
                "{} {} - {}".format(res.status_code, res.reason, res.request.url)
            )

    def authentication_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    # レポート一覧取得: https://docs.joinmastodon.org/methods/admin/reports/#get
    # デフォルトでは未解決のもののみ返す。
    # resolved=Trueで解決済みのものを返す。
    def get_reports(self, limit: int = 5, resolved: bool = False) -> dict:
        uri = f"{self.don_url}/api/v1/admin/reports"
        params = {"limit": str(limit)}
        if resolved:
            params["resolved"] = "1"
        res = requests.get(
            uri,
            headers=self.authentication_header(),
            params=params,
        )
        if self.response_validator(res):
            return res.json()

    # サスペンド: https://docs.joinmastodon.org/methods/admin/accounts/#action
    def suspend(self, target_id: str, report_id: str) -> dict:
        uri = f"{self.don_url}/api/v1/admin/accounts/{target_id}/action"
        res = requests.post(
            uri,
            headers=self.authentication_header(),
            data={"type": "suspend", "report_id": report_id},
        )
        if self.response_validator(res):
            return res.json()

    # レポート解決: https://docs.joinmastodon.org/methods/admin/reports/#resolve
    # サスペンド時にreport_idを付与しておけば自動的に解決されるので、
    # 通常は個別に処理する必要はない。
    def resolve_report(self, report_id: str) -> dict:
        uri = f"{self.don_url}/api/v1/admin/reports/{report_id}/resolve"
        res = requests.post(
            uri, headers=self.authentication_header(), data={"report_id": report_id}
        )
        if self.response_validator(res):
            return res.json()


auto_resolver = AutoSpammerResolver(
    don_url=config["DonURL"], access_token=config["AccessToken"]
)


# 始末するターゲットであればTrue、始末しなくてもよければFalseを返す。
# 状況に応じて書き換えていく。
def target_check(report: dict) -> bool:
    # spamカテゴリで報告されたもの以外は自動処理しない
    if report["category"] != "spam":
        return False

    # ターゲットユーザ名の長さが10文字以外の場合は自動処理しない
    if len(report["target_account"]["username"]) != 10:
        return False

    # 自身のサーバ以外から(外部サーバから)のレポートである場合は自動処理しない
    if report["account"]["domain"] is not None:
        return False
    return True


resolved = False
if len(sys.argv) == 2 and sys.argv[1] == "resolved":
    resolved = True

# 直近50件の未解決レポートを取得する。
for report in auto_resolver.get_reports(limit=50, resolved=resolved):
    print("-" * 10)
    print(f"ReportID: {report['id']}")
    print(f"Category: {report['category']}")
    print(f"ActionTaken: {report['action_taken']}")
    print(f"TakenAt: {report['action_taken_at']}")
    print(f"Comment: {report['comment']}")
    print(f"Forwarded: {report['forwarded']}")
    print(f"CreatedAt: {report['created_at']}")
    print(f"UpdatedAt: {report['updated_at']}")
    print(f"Reporter: {report['account']['username']}@{report['account']['domain']}")
    print(
        f"Target: {report['target_account']['username']}@{report['target_account']['domain']} ({report['target_account']['id']})"
    )
    print(f"Suspended: {report['target_account']['suspended']}\n")
    if not target_check(report):
        print("Skipped.")
        continue
    # 対象アカウントをサスペンドする。
    if len(sys.argv) == 2 and sys.argv[1] == "execute":
        auto_resolver.suspend(
            target_id=report["target_account"]["id"], report_id=report["id"]
        )
        # suspend処理の際にreport_idを付けとくと、別途resolveしなくてもいいらしい
        # auto_resolver.resolve_report(report_id=report['id'])
        print("Executed.")
