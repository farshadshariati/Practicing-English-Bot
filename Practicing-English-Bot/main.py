import json
import time

from threading import Thread
from models import Reminder, current_date_util
from telegram_api import Bot
from database import Session, Base, engine
from sqlalchemy import select
from models import User
from processors import process_message, process_status
import updated

TOKEN = "****"

commands = {
    'sign up': 'use this commands to sign up in bot',
    'settings': 'to use reminder',
    'word practice': 'type to start words practice'
}


# Control of what to
# do with Updates

def main(bot: Bot):
    # getting updates
    try:
        updates = bot.get_updates(10)
        if len(updates['result']) <= 0:
            time.sleep(1)
            return
    except Exception as exp:
        print('something happened when getting updates waiting 30 seconds')
        print(exp)
        time.sleep(10)
        return

    # process the update
    for update in updates['result']:
        if update.get('message'):
            chat_id = update['message']['chat']['id']
        elif update.get('callback_query'):
            chat_id = update['callback_query']['message']['chat']['id']
        else:
            # other inputs are not supported
            return

        # loading user
        with Session(expire_on_commit=False) as session, session.begin():
            stmt = select(User).filter(User.user_id == chat_id)
            user = session.scalar(stmt)
            if user is None:
                bot.send_message(chat_id, 'welcome')
                new_user = User(user_id=chat_id)
                session.add(new_user)
                return

        if update.get('message'):
            message = update['message']['text']

            if not process_message(bot, user, message, chat_id):
                # process_status
                process_status(bot, user, message, chat_id)

        elif update.get('callback_query'):
            callback_query = update['callback_query']['data']
            if callback_query is not None:
                with Session() as session, session.begin():
                    tmp_message = None
                    if callback_query == 'word practice practice':
                        user.status = "word practice practice"

                    elif callback_query == 'word practice review':
                        user.status = "word practice review"

                    elif callback_query == 'subject practice practice':
                        user.status = "subject practice practice"

                    elif callback_query == 'subject practice review':
                        user.status = "subject practice review"

                    elif callback_query == 'sentence practice practice':
                        user.status = 'sentence practice practice'

                    elif callback_query == 'sentence practice review':
                        user.status = 'sentence practice review'

                    elif callback_query == 'go right my':
                        tmp_message = 'go right my'
                    elif callback_query == 'go left my':
                        tmp_message = 'go left my'
                    elif callback_query == 'go right other':
                        tmp_message = 'go right other'
                    elif callback_query == 'go left other':
                        tmp_message = 'go left other'

                    session.add(user)
                    if tmp_message is None:
                        process_status(bot, user, '', chat_id)
                    else:
                        process_status(bot, user, tmp_message, chat_id,
                                       update['callback_query']['message']['message_id'])


# this def checks the reminders and sends a notification on time
def reminder(bot: Bot):
    #  todo test and debug
    while True:
        # if current_date_util().now().minute == 0:
        with Session() as session, session.begin():
            data = session.query(Reminder).all()
            for reminder in data:
                if reminder.hour == current_date_util().now().hour:
                    bot.send_message(reminder.user.user_id)
        time.sleep(60)


if __name__ == "__main__":
    # read_settings
    Base.metadata.create_all(engine)
    session = Session()
    bot = Bot(TOKEN)
    t1 = Thread(target=reminder, args=(bot,))
    # t1.start()
    while True:
        try:
            main(bot)
        except Exception as e:
            print(e)
            time.sleep(3)
            continue
    # t1.join()
