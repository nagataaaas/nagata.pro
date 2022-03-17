---
title: "Dockerのubuntuでcronを起動する"
date: 2022-03-16T02:47:09+09:00
draft: false
tags: [docker, ubuntu]
categories: [Docker]
description: Docker Ubuntuでcronを起動する
---

# TL;DR

Docker Ubuntuでcronが動作せずに悩んでる人は、以下のように変更することで、動作させることができる。

最後の`CMD`はやめて、`RUN cron -f &`とかに変更しても大丈夫。

```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install cron

RUN echo '* * * * * echo Hello World >  /var/log/cron.log' > /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]
```

## なぜ困ったか

このサイトはDocker内で[Hugo](https://gohugo.io/) を使いサーバーを建てて起動しています。

ちょうど[メインページ](/)に[GitHub](https://github.com/) のAPIから取得した、repo情報を表示するところがあるのですが、これを定期的にリフレッシュしたくてcronを使うことにしました。

staticフォルダ内にAPIから取得したjsonを保存しておくと、それが変更されたときにrebuildされるので最新の情報にしておくことができるというわけです。

そのため、cronを用いて

    # 毎時0分にAPIから取得したjsonを保存する
    0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json

みたいなものを設定することで、リフレッシュ出来るわけです。
しかし、(これは知らなかったんですが)Docker内ではデフォルトでcronを使えません(少なくともubuntu:18.04では)。

そのため、いろいろ試したんですが、cronがどうにも実行されない？

漁りに漁ってようやく見つけたのがこのリポジトリです。

{{< github_card username="thelebster" repo="docker-cron" >}}

これを見つけるまでに、私は以下のようなものを試して上手くいきませんでした

```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y cron --no-install-recommends

# setting cron
RUN echo '0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json' >> /etc/crontab
RUN cron -f &
```

だったり

```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y cron --no-install-recommends

RUN /etc/init.d/cron start
RUN crontab -l > /crontab.txt
RUN echo '0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json' >> /crontab.txt
RUN crontab /crontab.txt
RUN rm /crontab.txt
```

具体的にどれが原因なのかはわかっていませんが、考えられる問題点は

- cron インストール時に `--no-install-recommends` オプションを指定している
- /etc/cron.d/crontab の権限が違う？
- /usr/bin/crontab 自体の実行をしていない

とかですかね？
私はLinuxは門外漢なのであまりよくわからないですが、`--no-install-recommends` オプションを指定すると正しく動作しない場合があるのでしょうか。。。

とにかく、cronを動かすためには、[この](#tldr)ようにしなければならないということでした。