#!/bin/sh

cd /hugo || exit

wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >/hugo/static/github_repos.json
echo cron starting
cron -f &
echo cron started
hugo server --bind 0.0.0.0 --port 80 --disableLiveReload -b "https://nagata.pro"