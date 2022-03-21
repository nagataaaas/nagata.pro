---
title: "メールサーバーを建てる【WebARENA Indigo + Mailu + Cloudflare】"
date: 2022-03-21T15:13:48.559Z
draft: false
tags: [email, webarena-indigo, mailu, cloudflare, docker]
categories: [email-server]
ShowToc: true
description: WebARENA IndigoのVPSを契約して、Dockerを用いてMailuを起動。CloudflareのDNSを使って、メールサーバーを建てる。
---

# 選定理由
## WebArena Indigo
結論からいうと、**圧倒的コスパ**です

もともとは[さくらのVPS](https://vps.sakura.ad.jp/) でメールサーバーを建てる予定でしたが、Mailuをウイルス対策ソフト等を込みで起動するには
3GB以上のメモリが必要でした。

執筆時点(2022年3月)では、メモリを3GB以上にすると、もっとも安い石狩リージョンでも **3,530円/月** になります。

それはちょっと高いなぁ。。。と思っているところに、ふと以前お客さんが[WebARENA Indigo](https://web.arena.ne.jp/indigo/price/) のVPSを使用されていたことを思い出し調べてみると、
従量課金制なのですが

- メモリ4GB
- SSD80GB

で、ずっと起動していても最大 **1,272円/月** です。

1/3程度の価格で、SSD容量こそ少ないですが、メールサーバーということを考えればこちらの方がずいぶん良い選択でした。

## Mailu

公式サイトの言葉を借りると

> Mailu is a simple yet full-featured mail server as a set of Docker images. \
> It is free software (both as in free beer and as in free speech), open to suggestions and external contributions. \
> The project aims at providing people with an easily setup, easily maintained and full-featured mail server while not shipping proprietary software nor unrelated features often found in popular groupware.
> 
> 訳:\
> Mailuはシンプルかつ全ての昨日をそなえたDockerイメージです。\
> フリーソフトで、外部のコントリビューションと提案を受け付けています。\
> 簡単にセットアップ、メンテナンスできる完全な機能をもつメールサーバーを提供することを目的としており、よくあるグループウェアのようにブラックボックスなソフトや無関係な機能を使用することはありません。

ということで、すごく使いやすそうですね。

具体的には

- IMAP, IMAP+, SMTP　などのスタンダードなメールサーバー
- エイリアス、ドメインエイリアス、カスタムルーティング
- Webからアクセスできる管理者画面
- オートリプライ、オートフォワード
- TLS, Let's Encryptによる自動署名、DKIM、ウイルス対策
- greylisting, DMARC, SPFなどのスパム対策

がサポートされています。

しかも、GUIでポチポチするだけで設定ファイルを作成することができます。
最高ですね！

<p style="opacity: 0.5">もとは<a href="https://github.com/docker-mailserver/docker-mailserver">Docker-Mailserver</a>を使おうと思ってあれやこれやしていたのですが、公式の通りにやってもメール受信がどうにも上手くいかなかったので諦めました。</p>

## Cloudflare
これは、もともとの個人サイト(このサイト)を建てるときに使ったものです。

ドメインを卸値で購入できるので、[Cloudflare Register](https://www.cloudflare.com/ja-jp/products/registrar/) でドメイン購入をして、その勢いでDNSも設定しています。

# サーバーを建てる
## 環境構築
OSはUbuntu18.04を選択。

WebArena Indigoはコンソールにwebからアクセスできる機能を提供しています。[ここ](https://web.arena.ne.jp/indigo/spec/login.html) によると、初回起動時には

- ユーザ名: ubuntu
- パスワード: なし(何も入力せずエンター)

でログインできるようですが、どうにも失敗するので、sshで手元から接続することにしました。

```shell
# gitなどインストール
sudo apt-get update
sudo apt-get install -y git vim curl wget unzip zip gnupg lsb-release ca-certificates

# dockerインストール
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# docker-composeインストール
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

として[docker-compose](https://docs.docker.jp/compose/overview.html) のインストールまで済ませます。

## Mailuのセットアップ
[Mailu configuration](https://setup.mailu.io/1.9/) を使って、GUIから設定を行うことができます。

<details><summary>
英語なので、以下に簡単に説明を残しておきます。
</summary>

1. **Pick a flavor**: サーバの建て方。
   1. **Compose**: Docker Compose を使う方法。こっちの方が個人的におすすめ
   2. **Stack**: Docker Swarm を使う方法
2. **Mailu storage path**: 設定ファイルやメールデータを保存する場所。実行ディレクトリにもなる。デフォルトのままで良いと思う
3. **Main mail domain and server display name**: メールのドメイン。例えば、 __test@mail.test.com__ というメールアドレスにしたいなら、mail.test.com にする
4. **Postmaster local part**: いろいろ重要なメールが __{この値}@{3で入力したドメイン}__ に届く。デフォルトのままでいいと思う
5. **Choose how you wish to handle security TLS certificates**: TLSに使う証明書を作成する方法。デフォルトのままでいいと思う
   1. **Authentication rate limit per IP for failed login attempts or non-existing accounts**: 1時間当たりのログイン失敗のレートリミット
   2. **Authentication rate limit per user**: ユーザあたりの1日のログインレートリミット
   3. **Outgoing message rate limit (per user)**: ユーザ当たり、1日に何通まで送れるか
6. **Opt-out of statistics**: 統計情報のオプトアウト。多分オンにすると、統計情報をMailuに提供する？
7. **Website name**: ウェブサイトの名前を紐づけられる。管理画面の名前とかにもなる
8. **Linked Website URL**: ウェブサイトのリンクを紐づけられる。
9. **Enable the admin UI (and path to the admin UI)**: 管理者画面を有効にする。管理者画面のパスも決められる。有効にした方が、あとあと便利だと思うけど、セキュリティ的に怖い人は切ってても良いかも。私は個人メールだからと割り切って有効にしました。
10. **Enable Web email client (and path to the Web email client)**: ウェブからアクセスできるメールクライアントを立ち上げるか。パスも変更できる。[roundcube](https://roundcube.net/) と[rainloop](https://www.rainloop.net/) が選べる。roundcubeはUIが古臭い(ごめんなさい)イメージがあったけれど、1.4.0でモダンなUIに変更されたので、こちらにしました。
11. **Enable the antivirus service**: ウイルス対策を有効にするか。有効にした方がいいと思うけど、メモリを1GB喰うので、慎重に。
12. **Enable the Webdav service**: Webdavを有効にして、連絡先とかカレンダー情報を保存できる。あると便利だけど無くてもいい。
13. **Enable fetchmail**: 外部のメールアカウントのメールを引っ張ってこっちで見れるようにするか。メールの引っ越しの時は使うといいかも。
14. **IPv4 listen address**: バインドするアドレス。VPSで使う時は、`0.0.0.0`でいいの？教えて偉い人
15. **Subnet of the docker network. This should not conflict with any networks to which your system is connected. (Internal and external!)**: Dockerで使うネットワークのサブネット。他のものと衝突しちゃダメ
16. **Enable IPv6**: IPv6を有効にするか
17. **Enable an internal DNS resolver(unbound)**: (多分)ドメインを内部でまた確認するかどうか
18. **Public hostnames**: ホストネームの一覧。
19. **Database preference**: どのデータベースバックエンドを使うか。mysqlが安定するような気がするけど、個人的にsqliteのシンプル感が好きなのでsqlite
</details><br>

全て入力し終わったら、**Setup Mailu**を入力し表示されるステップをふむと、公開することができます。

セッティングが終わったら

```shell
# サーバーをまず立てる
$ sudo docker-compose -p mailu up -d

# まず1つユーザを作らないとサーバに接続できない。
# 以下のコマンドで admin1@test.com というアカウントを PassWord というパスワードで作成できる
$ sudo docker-compose -p mailu exec admin flask mailu admin admin1 test.com PassWord

# 以下のコマンドで、管理者権限のない nagata@test.com というアカウントも作れる
$ sudo docker-compose exec admin flask mailu user nagata test.com PassWord2
```

# DNSの設定
サーバが作成出来たら、DNSの設定に移っていきます。

## 最低限のルーティングなど

### Aレコード
Aレコードを用いて、メールアドレスの@以降の部分を、上で建てたサーバに向けます

```text
mail.test.com.	1	IN	A	144.144.144.144
```

Cloudflareであれば、

| Type | Name | Content         | Proxy Status     | TTL  |
|------|------|-----------------|------------------|------|
| A    | mail | 144.144.144.144 | DNS only (グレーの雲) | Auto |

のように設定しました。

**mail.test.com**ではなく**test.com**で作ることもできますが、**mail.** にしたほうがいい感じがします。(いい感じ？)

### MXレコード
メールに関する名前解決を設定します。

```text
mail.test.com.	1	IN	MX	0 mail.test.com.
```

Cloudflareであれば

| Type | Name | Content       | Proxy Status | TTL  |
|------|------|---------------|--------------|------|
| MX   | mail | mail.test.com | DNS only     | Auto |

となります。

**test.com** に送られたメールも受け取りたいのであれば、

```text
mail.test.com.	1	IN	MX	10 mail.test.com.
```
か

| Type | Name | Content       | Proxy Status | TTL  |
|------|------|---------------|--------------|------|
| MX   | @    | mail.test.com | DNS only     | Auto |

も追加しておき、Mailuの管理者画面から`メールドメイン > 代替ドメイン(管理タブ)`に`test.com`を追加することで受け取れるようになります。

## 証明関係
以上の設定では、DKIMやSPFの設定ができていません。
つまり、迷惑メールに振り分けられたり、そもそも受け取ってくれない可能性があります(gmailは受け取ってくれませんでした)。

なので、適切に情報を設定します。

管理者画面から`メールドメイン > 詳細(操作タブ)`を開き、**鍵を再生成** して、適切なエントリを生成します。

DKIM公開鍵以外の全てをDNSに設定することで、証明を行うことできます。

CloudflareはGUI入力なので大変ですが、全てをコピーしてメモ帳なんかでtxtファイルにまとめた後、**Advanced**から読み込むことで一気に追加できます。

# テスト
適当なGmailアカウントに送信して、迷惑メールに振り分けられていないことを確認すれば大体大丈夫だと思いますが、より詳細に知るには、以下のサイトがお勧めです。

[https://www.appmaildev.com/jp/dkim](https://www.appmaildev.com/jp/dkim)

**次のステップ** を押下後、表示されるメールアドレスにメールを送信してください。

![](static/appmaildev.png "www.appmaildev.com")

このようにそれぞれのテストに通過したかどうかを教えてくれるので、間違っていれば簡単に修正できます。

# おわりに

このような手順を踏むことで、簡単にメールサーバーを構築できます。

非常におすすめですので、ぜひ試してみてください。