# AutoSpammerResolver

## これはなに?
Mastodonでユーザーにより報告されたspamを、問答無用で始末(サスペンド)するスクリプトです。
利用には下記の権限が必要です。

- admin:read:reports
- admin:write:accounts
- admin:write:reports


## つかいかた
「開発」 -> 新規アプリから、アプリを作成してください。

- アプリの名前: てきとうに名前を付ける
- アプリのウェブサイト: 空欄
- リダイレクトURI: urn:ietf:wg:oauth:2.0:oob
- アクセス権
  - admin:read:reports
  - admin:write:accounts
  - admin:write:reports

作成できたら、生成された**アクセストークン**を、
config.jsonの**AccessToken**に記述してください。
また、DonURLを自身が管理しているMastodonサーバのURLにしてください。

```json
{
  "DonURL": "https://social.mikutter.hachune.net",
  "AccessToken": "生成されたアクセストークン"
}
```

### 未解決の報告を確認する
実行すると、下記のように対象者の情報が表示されます。
デフォルトでは最新50件分を処理します。

```sh
% python3 AutoSpammerResolver.py
ReportID: 1341
Category: spam
ActionTaken: True
TakenAt: 2024-02-17T16:47:32.955Z
Comment:
Forwarded: True
CreatedAt: 2024-02-17T16:31:08.772Z
UpdatedAt: 2024-02-17T16:47:32.958Z
Reporter: reporter_name@None
Target: target_user@target_domain (111947772733136565)
Suspended: False
...
```

### 始末する
実際に始末する際は、`execute`オプションを付けて実行してください。
```sh
% python3 AutoSpammerResolver.py execute
ReportID: 1341
Category: spam
ActionTaken: True
TakenAt: 2024-02-17T16:47:32.955Z
Comment:
Forwarded: True
CreatedAt: 2024-02-17T16:31:08.772Z
UpdatedAt: 2024-02-17T16:47:32.958Z
Reporter: reporter_name@None
Target: target_user@target_domain (111947772733136565)
Suspended: False

Executed.
```
始末すると、対象となったアカウントはサスペンドされ、
レポートにも解決フラグが設定されます。


### 解決済みのレポートを確認する

既に解決済みのレポートを確認したい時は、`resolved`オプションを付けて実行してください。

```sh
% python3 AutoSpammerResolver.py resolved
ReportID: 1341
Category: spam
ActionTaken: True
TakenAt: 2024-02-17T16:47:32.955Z
Comment:
Forwarded: True
CreatedAt: 2024-02-17T16:31:08.772Z
UpdatedAt: 2024-02-17T16:47:32.958Z
Reporter: reporter_name@None
Target: target_user@target_domain (111947772733136565)
Suspended: True
```

## カスタマイズ
`target_check`メソッドを変更すると、対象を絞り込んだりできます。
デフォルトでは、下記の条件を全て満たしたもののみ自動で処理します。

- 報告者は自インスタンスのもののみ(スパム報告スパム対策)
- 対象ユーザー名は10文字のもの
- spamとして報告されたもの
