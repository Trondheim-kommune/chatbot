# This file should be called every 24 hours by cron. This deletes the previous
# scraped data and scrapes again
# To insert this into cron use the command: `crontab -e` and insert this line:
# `0 0 * * *  bash <path_to_this_script>`
cd /usr/src/app
rm scraper/scraped.json
bash launch.sh
