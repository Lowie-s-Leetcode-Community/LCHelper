while true; do
    git pull
    python3 bot.py

    (( $? != 42 )) && break

done