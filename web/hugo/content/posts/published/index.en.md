---
title: "Running cron in Docker ubuntu"
date: 2022-03-16T02:47:09+09:00
draft: false
tags: [docker, ubuntu]
categories: [Docker]
description: Had some trouble running cron in Docker ubuntu. But I found a solution.
--- ...

# TL;DR
If you are having trouble with cron not working on Docker Ubuntu, you can make it work by making your Dockerfile like below.

You can stop using `CMD` at the end and change it to `RUN cron -f &` or something like that.
```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install cron

RUN echo '* * * * * echo Hello World > /var/log/cron.log' > /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]
```

## Why I'm in trouble

This website is built and running in Docker using [Hugo](https://gohugo.io/).

I decided to use cron to refresh the repo information obtained from the [GitHub](https://github.com/) API on the [main page](/).

If I store the json retrieved from the API in the static folder and make some change, Hugo will rebuild the entire website, so I can keep it up-to-date.

Therefore, I used cron like this:

    # Save json retrieved from API every hour at 0 minute
    0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json

So you can refresh the repo information every hour.

However, (and I didn't know this), you can't use cron by default within Docker (at least ubuntu:18.04).

So I've tried everything, but cron is not running in any way.

After much searching, I finally found this repository.

{{< github_card username="thelebster" repo="docker-cron" >}}

Before I found this, I tried the following without success

```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y cron --no-install-recommends

# setting cron
RUN echo '0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json' >> /etc/crontab
RUN cron -f &
````

or

```dockerfile
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y cron --no-install-recommends

RUN /etc/init.d/cron start
RUN crontab -l > /crontab.txt
RUN echo '0 * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /static/github_repos.json' >> /crontab.txt
RUN crontab /crontab.txt
RUN rm /crontab.txt
```

I don't know exactly which one is causing the problem, but possible issues are

- The `--no-install-recommends` option is specified during cron installation.
- Wrong permissions for /etc/cron.d/crontab?
- Didn't run /usr/bin/crontab

I'm new to Linux, so I don't know much about it, but I wonder if the `--no-install-recommends` option might not work correctly.

Anyway, I had to do [this](#tldr) to get cron to work.