#!/usr/bin/env python3

import json
from argparse import ArgumentParser
from lib.SpammerResolver import SpammerResolver


config = json.loads(open("config.json", "r").read())
parser = ArgumentParser()
subcmd = parser.add_mutually_exclusive_group()
subcmd.add_argument(
    "--execute",
    action="store_true",
    default=False,
    help="報告されたターゲットを実際に始末する。",
)
subcmd.add_argument(
    "--resolved",
    action="store_true",
    default=False,
    help="解決済みレポートの一覧を見る。",
)
parser.add_argument(
    "--limit",
    dest="limit",
    default=50,
    help="一度に処理するレポート数。デフォルトは50件。",
)
parser.add_argument(
    "--max_id",
    dest="max_id",
    default=None,
    help="このIDより前に作成されたレポートを参照する。",
)

options = parser.parse_args()
resolver = SpammerResolver(don_url=config["DonURL"], access_token=config["AccessToken"])


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

    # 自身のサーバ内のユーザーがターゲットとなっている場合は自動処理しない
    if report["target_account"]["domain"] is None:
        return False

    # 以前に作られたアカウントの場合は自動処理しない
    if not resolver.after_x_day(report["target_account"]["created_at"]):
        return False

    return True


# 直近50件の未解決レポートを取得する。
for report in resolver.get_reports(
    limit=options.limit, resolved=options.resolved, max_id=options.max_id
):
    reporter_account = f"{report['account']['username']}@{report['account']['domain']}"
    target_account = (
        f"{report['target_account']['username']}@{report['target_account']['domain']}"
    )
    print("-" * 10)
    print(f"ReportID: {report['id']}")
    print(f"Category: {report['category']}")
    print(f"ActionTaken: {report['action_taken']}")
    print(f"TakenAt: {report['action_taken_at']}")
    print(f"Comment: {report['comment']}")
    print(f"Forwarded: {report['forwarded']}")
    print(f"CreatedAt: {report['created_at']}")
    print(f"UpdatedAt: {report['updated_at']}")
    print(f"Reporter: {reporter_account}")
    print(f"Target: {target_account} ({report['target_account']['id']})")
    print(f"TargetDomain: {report['target_account']['domain']}")
    print(f"Suspended: {report['target_account']['suspended']}\n")
    if not target_check(report):
        print(f"Skipped - Target: {target_account}, Reporter: {reporter_account}")
        continue
    print(f"Targetted - Target: {target_account}, Reporter: {reporter_account}")

    # 対象アカウントをサスペンドする。
    if options.execute:
        resolver.suspend(
            target_id=report["target_account"]["id"], report_id=report["id"]
        )
        # suspend処理の際にreport_idを付けとくと、別途resolveしなくてもいいらしい
        # auto_resolver.resolve_report(report_id=report['id'])
        print(f"Executed - Target: {target_account}, Reporter: {reporter_account}")
