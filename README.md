# LCHelper

Repo for LLC Assistant bot - A Discord bot built for Lowie's LeetCode Community (LLC) and all other stuff.

The database currently in use is `PostgreSQL`, and the library wrapper for the bot is `discord.py 2.0+`.

## Features

... In refactoring

## Installation

### 1. Clone the repository

Clone the repo using GUI or command line:
- If you have ssh set up: `git clone git@github.com:Lowie-s-Leetcode-Community/LCHelper.git`
- If you don't: `git clone https://github.com/Lowie-s-Leetcode-Community/LCHelper.git`

### 2. Library

Make sure you have Python when running this:
Run: `pip install -r requirements.txt`

### 3. Database

Clone the web app to somewhere else: [llc-webapp](https://github.com/Lowie-s-Leetcode-Community/llc-webapp)
Follow part 1, 2, 3 in README.md in llc-webapp to set up postgreSQL

### 4. Create an app in discord.com/developer

Go to [discord.com/developers](https://discord.com/developers/docs/intro) to create the bot:
- Create a new application
- In the OAuth2 part, save the `Client ID` and `Client secret` somewhere for the section below. Note that the "Client secret" will only show up 1 time, if you want to get it again, it will generate a new one.

### 5. Set up .env file

Copy .env.template file to .env file and edit:
- BOT_TOKEN: the `Client ID` you get from discord.com/developer 
- CLIENT_SECRET: the `Client secret` of the bot from discord.com/developer
- POSTGRESQL_CRED: change 12345678 to your postgres password, lc_db to the schema's name
- POSTGRESQL_SCHEMA: schema's name
- BOT_PREFIX: depends on you
Leave the rest alone.

### 6. Run the bot

- To simply start LCHelper, just run:

```sh
python bot.py
```

- To automatically pull from the repo and start the bot, run:

```sh
./run.sh
```

## Documentations

- To learn more about discord.py: [discordpy.readthefuckingdocs](https://discordpy.readthedocs.io/en/latest/index.html#manuals)
- To learn more about sql in python: [sqlalchemy](https://www.sqlalchemy.org/)
- The command does use both normal commands (prefix) and slash commands. Make sure you are familiar with command tree, slash commands and interaction:
  - [Bot commands tree and syncing guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)
  - [Bot interaction guide](https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f)
- Just-in-case guidelines: [python guide](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

## License

[MIT](https://choosealicense.com/licenses/mit/)

Made with 🧡 by Lowie's Leetcode Community Bot Development Team.

## Note Jan 25: have to add instruction to install psycopg2. :)
