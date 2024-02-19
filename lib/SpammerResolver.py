import requests
from datetime import datetime, timezone
from requests import Response


class SpammerResolver:
    class ProtocolError(Exception):
        pass

    def __init__(self, don_url: str, access_token: str):
        self.don_url = don_url
        self.access_token = access_token

    def response_validator(self, res: Response) -> bool:
        if res.status_code == 200:
            return True
        else:
            raise SpammerResolver.ProtocolError(
                "{} {} - {}".format(res.status_code, res.reason, res.request.url)
            )

    def authentication_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    # レポート一覧取得: https://docs.joinmastodon.org/methods/admin/reports/#get
    # デフォルトでは未解決のもののみ返す。
    # resolved=Trueで解決済みのものを返す。
    def get_reports(
        self, limit: int = 5, max_id: str | None = None, resolved: bool = False
    ) -> dict:
        uri = f"{self.don_url}/api/v1/admin/reports"
        params = {"limit": str(limit)}
        if max_id:
            params["max_id"] = max_id
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

    # スパムを通報し、元サーバへも通報を転送する。
    def write_spam_report(self, account_id: str, status_id: str) -> dict:
        uri = f"{self.don_url}/api/v1/reports"
        res = requests.post(
            uri,
            headers=self.authentication_header(),
            data={
                "account_id": account_id,
                "status_ids[]": status_id,
                "category": "spam",
                "forward": "1",
            },
        )
        if self.response_validator(res):
            return res.json()

    def after_x_day(self, created_at: str):
        created_t = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        x_day = datetime(2024, 2, 15, 0, 0, 0, tzinfo=timezone.utc)
        if created_t >= x_day:
            return True
        return False
