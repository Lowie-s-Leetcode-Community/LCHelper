# LCHelper
Repo for LCHelper bot - A Discord bot built for LLC, LeetCode queries and all other stuff.

The database currently in use is MongoDB.

PRs and issues are appreciated, and I will try to look into them often.

# Features
The features of the bot are separated into a number of cogs, which are also sorted in their respective folders. 

## LeetCode cogs
- **Onboarding**: Guides new users into LLC.
- **Features**: Provides LeetCode-related commands for LLC members.
- **Daily**: Handles LeetCode's Daily Challenge.
- **Crawling**: "Crawls" recent successful LeetCode submissions.
- **Logging**: Logs entries such as scoring, kick/ban,...

## Other cogs
- These are mostly tools for my own personal needs.

# Installation

## 1. Have your Discord bot
- The bot should have all the necessary **Privileged Gateway Intents** enabled, and have the scope `applications.commands` when adding into servers in order to use Slash commands.

## 2. Clone the repository
```console
git clone https://github.com/HmmOrange/LCHelper
```

## 3. Library
LCHelper also requires the proper libraries in `requirements.txt` to work. Make sure to install all of them using:
```console
pip install lib_name
```

(I'll put it in `./run.sh` later, hopefully)

## 4. Environments
To make it easy to deploy the bot in different enviroments, LCHelper uses `dotenv`. First create a `.env` file, then put in all appropriate variables in the newly created file:

```js
BOT_TOKEN = 
MONGODB_LOGIN_CRED = 
BOT_PREFIX = 
START_UP_TASKS = 
```

The general MongoDB structure should be:
```
LC_db (Database)
⌊ LC_config (Collections)
⌊ LC_daily
⌊ LC_problems
⌊ LC_quiz
⌊ LC_users
```

## 5. `.gitignore`
To prevent cache or unnecessary files from being pushed to the main repository, a `.gitignore` file is highly recommended.

The file should include:
```
.env
.gitignore
__pycache__/
*.pyc
```

## 6. Run the bot
- To simply start LCHelper, just run:
```console
python bot.py
```

- To automatically pull from the repo and start the bot, run:
```
./run.sh
```

# Usage
- The command does use both normal commands (prefix) and slash commands. Make sure you are familiar with command tree, slash commands and interaction:
    - [Bot commands tree and syncing guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)
    - [Bot interaction guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)


# License
[MIT](https://choosealicense.com/licenses/mit/)