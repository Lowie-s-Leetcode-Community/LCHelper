# LCHelper

Repo for LCHelper bot - A Discord bot built for Lowie's LeetCode Community (LLC) and all other stuff.

The database currently in use is `MongoDB`, and the library wrapper for the bot is `discord.py 2.0+`.

PRs and issues are appreciated, and I will try to look into them often.

## Features

The features of the bot are separated into a number of cogs, which are also sorted in their respective folders.

- **Onboarding**: Guides new users into LLC.
- **Features**: Provides LeetCode-related commands for LLC members.
- **Daily**: Handles LeetCode's Daily Challenge.
- **Crawling**: "Crawls" recent successful LeetCode submissions.
- **Logging**: Logs entries such as scoring, kick/ban,...

## Installation

### 1. Have your Discord bot ready

- The bot should have all the necessary **Privileged Gateway Intents** enabled, and have the scope `applications.commands` when adding into servers in order to use Slash commands.

### 2. Clone the repository

```console
git clone https://github.com/HmmOrange/LCHelper
```

### 3. Library

LCHelper also requires the proper libraries in `requirements.txt` to work. Make sure to install all of them using:

```console
pip install lib_name
```

(I'll put it in `./run.sh` later, hopefully)

### 4. Environments

To make it easy to deploy the bot in different enviroments, LCHelper uses `dotenv`. First create a `.env` file, then put in all appropriate variables in the newly created file:

```js
BOT_TOKEN = 
MONGODB_LOGIN_CRED = 
BOT_PREFIX = 
START_UP_TASKS = 
```

- `BOT_TOKEN`: The token required for a Discord bot to run.
- `MONGODB_LOGIN_CRED`: An URL to connect to the MongoDB deployment.
- `BOT_PREFIX`: The bot's prefix.
- `START_UP_TASKS:` True/False - if the crawling and the daily tasks should start when running the bot. Should be set to `False` if you are running it locally to avoid conflicts.

The general MongoDB structure should be:

```text
LC_db (Database)
⌊ LC_config (Collections)
⌊ LC_daily
⌊ LC_problems
⌊ LC_quiz
⌊ LC_users
```

(Script to create a MongoDB sample should be added soon)

### 5. `.gitignore`

To prevent cache or unnecessary files from being pushed to the main repository, a `.gitignore` file is required.

The file should include:

```text
.env
__pycache__/
*.pyc
backup.json
```

### 6. Run the bot

- To simply start LCHelper, just run:

```sh
python bot.py
```

- To automatically pull from the repo and start the bot, run:

```sh
./run.sh
```

## Usage

- The command does use both normal commands (prefix) and slash commands. Make sure you are familiar with command tree, slash commands and interaction:
  - [Bot commands tree and syncing guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)
  - [Bot interaction guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)

## License

[MIT](https://choosealicense.com/licenses/mit/)

Made with 🧡 by Orange.

## Note Jan 25: have to add instruction to install psycopg2. :)
