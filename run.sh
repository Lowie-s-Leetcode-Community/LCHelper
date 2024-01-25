while true; do
    git pull origin master
    python3 bot.py

    (( $? != 42 )) && break

done