while true; do
    git pull
    python bot.py

    (( $? != 42 )) && break

done