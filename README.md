# AutoSpammerResolver

## これはなに?
Mastodonでユーザーにより報告されたspamを、問答無用で始末(サスペンド)するスクリプトと、
リモート公開ストリームに流れてくるスパムを自動的にレポートして始末(サスペンド)するスクリプトです。
利用には下記の権限が必要です。

- admin:read:reports 提出されたレポートの参照
- admin:write:accounts サスペンド処理
- admin:write:reports レポートの更新
- read:statuses 公開リモートタイムラインの参照
- write:reports レポートの提出

## AutoSpammerResolverのつかいかた
「開発」 -> 新規アプリから、アプリを作成してください。

- アプリの名前: てきとうに名前を付ける
- アプリのウェブサイト: 空欄
- リダイレクトURI: urn:ietf:wg:oauth:2.0:oob
- アクセス権
  - admin:read:reports
  - admin:write:accounts
  - admin:write:reports
  - read:statuses
  - write:reports

作成できたら、生成された**アクセストークン**を、
`config.json`の**AccessToken**に記述してください。
また、DonURLを自身が管理しているMastodonサーバのURLにしてください。

```json
{
  "DonURL": "https://social.mikutter.hachune.net",
  "AccessToken": "生成されたアクセストークン"
}
```

### 未解決の報告を確認する
実行すると、下記のように対象者の情報が表示されます。
デフォルトでは最新50件分を処理します。この制限は`--limit 10`のように変更できます(最大200件)。

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
実際に始末する際は、`--execute`オプションを付けて実行してください。
```sh
% python3 AutoSpammerResolver.py --execute
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

既に解決済みのレポートを確認したい時は、`--resolved`オプションを付けて実行してください。

```sh
% python3 AutoSpammerResolver.py --resolved
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

### カスタマイズ
`target_check`メソッドを変更すると、対象を絞り込んだりできます。


## Mabosstiffのつかいかた
`AutoSpammerResolver`と同様に`config.json`を作成し、`Mabosstiff.py`を実行するだけです。
サスペンドされたアカウントと投稿に関する情報は、blacklistディレクトリ以下にJSON形式で記録されます。
