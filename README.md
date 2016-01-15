#GitFetcher

Fetches from GitHub automatically.

##Usage

First, copy `config.py.example` to `config.py` and make changes as you need. Then, run the main program by typing `python3 main.py`. Then add repo's using `python3 AddRepo.py`, everything else that you may need will be shown when running that command. 

##Running Cronjob

edit your cron job using `crontab -e`. then add the following line: `*/5 * * * * python3 \<path\>/cronjob.py --dir=\<path\>` and it's done! Now, the GitFetcher will automatically restart if it get is not running.