#!/bin/sh

cd /hugo || exit

wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >/hugo/static/github_repos.json
echo cron starting
hugo -D -d /var/www/html
cron -f
# hugo server --bind 0.0.0.0 --port 80 --disableLiveReload -b "/"