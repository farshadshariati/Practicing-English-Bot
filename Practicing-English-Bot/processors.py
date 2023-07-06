import datetime

from models import User, Reminder, Userword, Sentence, Subject
from database import Session
from data_reader import get_words
from random import choice, choices
from models import localize_date_time
from similarity_check import text_similarity

commands = [
    'sign up',  # 'use this commands to sign up in bot'
    'settings',  # 'to use reminder',
    'word practice',  # 'type to start words practice'
    'sentence practice',  # sentence practice
    'subject practice'  # subject practice
]

cmd_keyboard = []
for item in commands:
    cmd_keyboard.append({'text': item})


def process_message(bot, user, message: str, chat_id):
    """
    processes the text sent from the user and answers accordingly if the command is available
    :return: True if the message was processed successfully else false
    """
    data = True
    if message == '/admin':
        with Session() as session, session.begin():
            user.status = "sending pass"
            bot.send_message(chat_id, 'please insert the password')
            session.add(user)

    elif message == '/start' or message == "sign up":  # first time
        with Session() as session, session.begin():
            if user is None:
                new_user = User(user_id=chat_id, status="sign up")
                session.add(new_user)
                bot.send_message(chat_id, 'enter your name and family name like:')
                bot.send_message(chat_id, 'علی محمدی')
            elif user.name is None or user.fname is None:
                user.status = "sign up"
                session.add(user)
                bot.send_message(chat_id, 'enter your name and family name like:')
                bot.send_message(chat_id, 'علی محمدی')
            else:
                bot.send_message(chat_id, 'welcome back', reply_markup={'keyboard': [cmd_keyboard]})
            # OTHER

    # settings
    elif message == 'settings':
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.status = "settings"
        bot.send_message(chat_id,
                         "enter a number from 0 to 24 anything outside this range will turn the reminder off")

    # word practice
    elif message == 'word practice':
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.status = "word practice"
            user_edited.current_input = ''
            user_edited.input_count = 0

        keyboard_inline = [
            [{'text': 'practice', 'callback_data': 'word practice practice'},
             {'text': 'review', 'callback_data': 'word practice review'}]
        ]
        bot.send_message(chat_id, "select what you want to do.", reply_markup={'inline_keyboard': keyboard_inline})

    elif message == 'subject practice':
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.status = "subject practice"
            user_edited.current_input = ''
            user_edited.input_count = 0

        keyboard_inline = [
            [{'text': 'practice', 'callback_data': 'subject practice practice'},
             {'text': 'review', 'callback_data': 'subject practice review'}]
        ]
        bot.send_message(chat_id, "select what you want to do.", reply_markup={'inline_keyboard': keyboard_inline})
    elif message == 'sentence practice':
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.status = "sentence practice"

        keyboard_inline = [
            [{'text': 'practice', 'callback_data': 'sentence practice practice'},
             {'text': 'review', 'callback_data': 'sentence practice review'}]
        ]
        bot.send_message(chat_id, "select what you want to do.", reply_markup={'inline_keyboard': keyboard_inline})

    else:
        data = False
    return data


def process_status(bot, user, message: str, chat_id, message_id=None):
    if user.status == 'sending pass':
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.status = None
            if message == 'mNs7hIf4AXF7':
                user.status = 'admin'
            session.add(user)

    elif user.status == "sign up":
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            user_edited.name = message.split(' ')[0]
            user_edited.fname = ' '.join(message.split(' ')[1:])
            user_edited.status = None

        bot.send_message(chat_id, "sign up successful", reply_markup={'keyboard': [cmd_keyboard]})

    elif user.status == "settings":
        with Session() as session, session.begin():
            user_edited = session.get(User, chat_id)
            try:
                hour = int(message)
            except ValueError as e:
                print(e)
                bot.send_message(chat_id, 'please insert a number')
                return e

            old = user_edited.reminder
            user_edited.reminder = None
            if old is not None:
                session.delete(old)
            msg = "reminder is now off"
            if 24 >= hour >= 0:
                user_edited.reminder = Reminder(hour=hour)
                msg = f"reminder at {hour}"

            user_edited.status = ""
        bot.send_message(chat_id, f"settings saved successfully\n{msg}")

    elif user.status == "word practice practice":
        words = get_words('ngram_freq_dict.csv')

        if user.input_count == 0 or user.input_count is None:
            word = choice(words)
            with Session() as session, session.begin():
                user = session.get(User, chat_id)
                while word in user.words:
                    word = choice(words)
                user.input_count = 1
                user.current_input = word
                session.add(user)
                session.add(Userword(user_id=chat_id, word=word))

                bot.send_message(chat_id, word, reply_markup={
                    'keyboard': [[{
                        'text': 'skip word',
                    }]]
                })

        elif not (user.input_count == 0 or user.input_count is None):
            if message == '' or message is None:
                bot.send_message(chat_id, 'error happened try again')
                with Session() as session, session.begin():
                    user = session.get(User, chat_id)
                    user.input_count = 0
                    session.add(user)
                return
            if message == 'skip word':
                word = choice(words)
                with Session() as session, session.begin():
                    user = session.get(User, chat_id)
                    while word in user.words:
                        word = choice(words)
                    bot.send_message(chat_id, word, reply_markup={
                        'keyboard': [[{
                            'text': 'skip word',
                        }]]
                    })
                    session.add(user)
            else:
                # save the word and sentence
                with Session() as session, session.begin():
                    the_word = session.query(Userword).filter(Userword.user_id == chat_id).filter(
                        Userword.word == user.current_input).first()
                    if the_word is None:
                        raise Exception("error there is no word in db")
                    session.add(Sentence(user_id=user.user_id, word_id=the_word.id, text=message))
                if user.input_count < 5:
                    word = choice(words)
                    with Session() as session, session.begin():
                        user = session.get(User, chat_id)
                        while word in user.words:
                            word = choice(words)
                        bot.send_message(chat_id, word, reply_markup={
                            'keyboard': [[{
                                'text': 'skip word',
                            }]]
                        })
                        user.input_count += 1
                        user.current_input = word
                        session.add(Userword(user_id=chat_id, word=word))
                        session.add(user)

                else:
                    with Session() as session, session.begin():
                        user.input_count = 0
                        user.status = None
                        session.add(user)
                    bot.send_message(chat_id, "nice job.",
                                     reply_markup={'keyboard': [cmd_keyboard]})
                    bot.send_message(chat_id, "this is the words from 7 days ago until now",
                                     reply_markup={'keyboard': [cmd_keyboard]})

                    date_begin = localize_date_time(datetime.datetime.now() - datetime.timedelta(days=7.3))
                    with Session() as session, session.begin():
                        db_words = session.query(Userword).filter(Userword.user_id == chat_id).filter(
                            Userword.created_at >= date_begin).all()
                        out = ''
                        for word in db_words:
                            out = out + word.word + " : " + word.sentence.text + "\n\n"
                        bot.send_message(chat_id, out)

        else:
            with Session() as session, session.begin():
                user = session.get(User, chat_id)
                user.input_count = 1
                session.add(user)

    elif user.status == "word practice review":

        keyboard_inline_my = [
            [
                {'text': '←', 'callback_data': 'go left my'},
                {'text': '→', 'callback_data': 'go right my'},
            ]
        ]

        if message is None or message == '':
            bot.send_message(chat_id, 'what to do', reply_markup={'keyboard': [[
                {
                    'text': 'my sentences'
                }
            ]]})

        elif message == 'my sentences':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                user_db.input_count = 1
                session.add(user_db)
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.word_id != None).order_by(
                    Sentence.created_at.desc()).limit(10).all()

                out = ''
                for sentence in sentences:
                    out = out + sentence.text + "\n\n"

            if len(out) <= 0:
                out = "not found"
                bot.send_message(chat_id, out, reply_markup={'keyboard': [cmd_keyboard]})
                return

            bot.send_message(chat_id, out,
                             reply_markup={'inline_keyboard': keyboard_inline_my, 'keyboard': [cmd_keyboard]})

        elif message == 'go right my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count + 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.word_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                if len(sentences) > 0:
                    user_db.input_count += 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                else:
                    out = "reached the ending"

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})

        elif message == 'go left my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count - 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.word_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                out = "reached the beginning"
                if current_page > 0:
                    user_db.input_count -= 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                elif current_page == 0:
                    user_db.input_count -= 1
                    session.add(user_db)

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})

        else:
            bot.send_message(chat_id, 'please select from commands', reply_markup={'keyboard': [cmd_keyboard]})

    elif user.status == "subject practice practice":

        if user.input_count == 0 or user.input_count is None:
            with Session() as session, session.begin():
                subjects = session.query(Subject).all()
                subject = choice(subjects)
                user = session.get(User, chat_id)
                user.input_count = 1
                user.current_input = subject.title
                session.add(user)

                bot.send_message(chat_id, subject.title, reply_markup={
                    'keyboard': [[{
                        'text': 'skip subject',
                    }]]
                })

        elif not (user.input_count == 0 or user.input_count is None):
            if message == '' or message is None:
                bot.send_message(chat_id, 'error happened try again')
                with Session() as session, session.begin():
                    user = session.get(User, chat_id)
                    user.input_count = 0
                    session.add(user)
                return
            if message == 'skip subject':

                with Session() as session, session.begin():
                    subjects = session.query(Subject).all()
                    subject = choice(subjects)
                    user = session.get(User, chat_id)
                    user.input_count = 1
                    user.current_input = subject.title
                    session.add(user)

                    bot.send_message(chat_id, subject.title, reply_markup={
                        'keyboard': [[{
                            'text': 'skip word',
                        }]]
                    })
                    session.add(user)
            else:
                # save the word and sentence
                with Session() as session, session.begin():
                    the_subject = session.query(Subject).filter(Subject.title == user.current_input).first()
                    session.add(Sentence(user_id=user.user_id, subject_id=the_subject.id, text=message))
                if user.input_count < 3:
                    with Session() as session, session.begin():
                        user = session.get(User, chat_id)
                        bot.send_message(chat_id, "insert next sentence.")
                        user.input_count += 1
                        session.add(user)

                else:
                    with Session() as session, session.begin():
                        user.input_count = 0
                        user.status = None
                        session.add(user)

                    bot.send_message(chat_id, "nice job.",
                                     reply_markup={'keyboard': [cmd_keyboard]})
                    bot.send_message(chat_id, "these are 5 sentences from other students",
                                     reply_markup={'keyboard': [cmd_keyboard]})

                    date_begin = localize_date_time(datetime.datetime.now() - datetime.timedelta(days=1))
                    with Session() as session, session.begin():
                        user_db = session.get(User, chat_id)
                        the_subject = session.query(Subject).filter(Subject.title == user_db.current_input).first()
                        db_sentences = session.query(Sentence).filter(Sentence.subject_id == the_subject.id) \
                            .filter(Sentence.user_id != chat_id).all()

                        if len(db_sentences) <= 0:
                            bot.send_message(chat_id, 'no sentences was found')
                            raise Exception("no words found")

                        k = 5 if len(db_sentences) >= 5 else len(db_sentences)

                        out = ''
                        for sentence in choices(db_sentences, k=5):
                            out = out + sentence.text + "\n\n"

                        bot.send_message(chat_id, out)

        else:
            with Session() as session, session.begin():
                user = session.get(User, chat_id)
                user.input_count = 1
                session.add(user)

    elif user.status == "subject practice review":

        keyboard_inline_my = [
            [
                {'text': '←', 'callback_data': 'go left my'},
                {'text': '→', 'callback_data': 'go right my'},
            ]
        ]

        keyboard_inline_other = [
            [
                {'text': '←', 'callback_data': 'go left other'},
                {'text': '→', 'callback_data': 'go right other'},
            ]
        ]

        if message is None or message == '':
            bot.send_message(chat_id, 'what to do', reply_markup={'keyboard': [[
                {
                    'text': 'my sentences'
                },
                {
                    'text': 'others sentences'
                }
            ]]})

        elif message == 'my sentences':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                user_db.input_count = 1
                session.add(user_db)
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).order_by(
                    Sentence.created_at.desc()).limit(10).all()

                out = ''
                for sentence in sentences:
                    out = out + sentence.text + "\n\n"

            if len(out) <= 0:
                out = "not found"
                bot.send_message(chat_id, out, reply_markup={'keyboard': [cmd_keyboard], 'keyboard': [cmd_keyboard]})
                return

            bot.send_message(chat_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})

        elif message == 'others sentences':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                user_db.input_count = 1
                session.add(user_db)
                sentences = session.query(Sentence).filter(Sentence.user_id != chat_id).order_by(
                    Sentence.created_at.desc()).limit(10).all()

                out = ''
                for sentence in sentences:
                    out = out + sentence.text + "\n\n"

            if len(out) <= 0:
                out = "not found"
                bot.send_message(chat_id, out, reply_markup={'keyboard': [cmd_keyboard]})
                return

            bot.send_message(chat_id, out,
                             reply_markup={'inline_keyboard': keyboard_inline_other, 'keyboard': [cmd_keyboard]})

        elif message == 'go right my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count + 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.subject_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                if len(sentences) > 0:
                    user_db.input_count += 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                else:
                    out = "reached the ending"

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})

        elif message == 'go left my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count - 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.subject_id is not None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                out = "reached the beginning"
                if current_page > 0:
                    user_db.input_count -= 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                elif current_page == 0:
                    user_db.input_count -= 1
                    session.add(user_db)

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})
        elif message == 'go right other':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count + 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.word_id is not None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                if len(sentences) > 0:
                    user_db.input_count += 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                else:
                    out = "reached the ending"

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_other})
        elif message == 'go left other':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count - 1
                sentences = session.query(Sentence).filter(Sentence.user_id != chat_id).filter(
                    Sentence.word_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                out = "reached the beginning"
                if current_page > 0:
                    user_db.input_count -= 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                elif current_page == 0:
                    user_db.input_count -= 1
                    session.add(user_db)
        else:
            bot.send_message(chat_id, 'please select from commands', reply_markup={'keyboard': [cmd_keyboard]})

    elif user.status == "sentence practice practice":

        if user.input_count == 0 or user.input_count is None:
            with Session() as session, session.begin():
                user = session.get(User, chat_id)
                user.input_count = 1
                session.add(user)
                bot.send_message(chat_id, 'insert a sentence')

        elif not (user.input_count == 0 or user.input_count is None):
            if message == '' or message is None:
                bot.send_message(chat_id, 'error happened try again')
                with Session() as session, session.begin():
                    user = session.get(User, chat_id)
                    user.input_count = 0
                    session.add(user)
                return
                # save the word and sentence
            if user.input_count < 3:
                with Session() as session, session.begin():
                    user = session.get(User, chat_id)
                    db_sentences = session.query(Sentence).filter((Sentence.subject_id == None)).filter(
                        (Sentence.word_id == None)) \
                        .distinct().all()
                    for sentence in db_sentences:

                        if len(sentence.text) <= 0:
                            continue
                        res = text_similarity(message, sentence.text)
                        if res >= 0.8:
                            bot.send_message(chat_id, "the sentence must be more distinct")
                            return
                    bot.send_message(chat_id, "insert next sentence.")
                    session.add(Sentence(user_id=user.user_id, text=message))
                    user.input_count += 1
                    session.add(user)

            else:
                with Session() as session, session.begin():
                    user.input_count = 0
                    user.status = None
                    session.add(user)

                bot.send_message(chat_id, "nice job.")
                bot.send_message(chat_id, "these are 5 sentences from other students",
                                 reply_markup={'keyboard': [cmd_keyboard]})

                date_begin = localize_date_time(datetime.datetime.now() - datetime.timedelta(days=1))
                with Session() as session, session.begin():
                    user_db = session.get(User, chat_id)
                    db_sentences = session.query(Sentence).filter(Sentence.subject_id == None) \
                        .filter(Sentence.user_id != chat_id).filter(Sentence.word_id == None).distinct().all()

                    if len(db_sentences) <= 0:
                        bot.send_message(chat_id, 'no sentences was found')
                        raise Exception("no words found")

                    k = 5 if len(db_sentences) >= 5 else len(db_sentences)

                    out = ''
                    for sentence in choices(db_sentences, k=5):
                        out = out + sentence.text + "\n\n"

                    bot.send_message(chat_id, out)

        else:
            with Session() as session, session.begin():
                user = session.get(User, chat_id)
                user.input_count = 1
                session.add(user)

    elif user.status == "sentence practice review":

        keyboard_inline_my = [
            [
                {'text': '←', 'callback_data': 'go left my'},
                {'text': '→', 'callback_data': 'go right my'},
            ]
        ]

        keyboard_inline_other = [
            [
                {'text': '←', 'callback_data': 'go left other'},
                {'text': '→', 'callback_data': 'go right other'},
            ]
        ]

        if message is None or message == '':
            bot.send_message(chat_id, 'what to do', reply_markup={'keyboard': [[
                {
                    'text': 'my sentences'
                },
                {
                    'text': 'others sentences'
                }
            ]]})

        elif message == 'my sentences':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                user_db.input_count = 1
                session.add(user_db)
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).order_by(
                    Sentence.created_at.desc()).limit(10).all()

                out = ''
                for sentence in sentences:
                    out = out + sentence.text + "\n\n"

            if len(out) <= 0:
                out = "not found"
                bot.send_message(chat_id, out, reply_markup={'keyboard': [cmd_keyboard]})
                return

            bot.send_message(chat_id, out,
                             reply_markup={'inline_keyboard': keyboard_inline_my, 'keyboard': [cmd_keyboard]})

        elif message == 'others sentences':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                user_db.input_count = 1
                session.add(user_db)
                sentences = session.query(Sentence).filter(Sentence.user_id != chat_id).order_by(
                    Sentence.created_at.desc()).limit(10).all()

                out = ''
                for sentence in sentences:
                    out = out + sentence.text + "\n\n"

            if len(out) <= 0:
                out = "not found"
                bot.send_message(chat_id, out, reply_markup={'keyboard': [cmd_keyboard]})
                return

            bot.send_message(chat_id, out,
                             reply_markup={'inline_keyboard': keyboard_inline_other, 'keyboard': [cmd_keyboard]})

        elif message == 'go right my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count + 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.subject_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                if len(sentences) > 0:
                    user_db.input_count += 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                else:
                    out = "reached the ending"

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})

        elif message == 'go left my':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count - 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.subject_id is not None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                out = "reached the beginning"
                if current_page > 0:
                    user_db.input_count -= 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                elif current_page == 0:
                    user_db.input_count -= 1
                    session.add(user_db)

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_my})
        elif message == 'go right other':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count + 1
                sentences = session.query(Sentence).filter(Sentence.user_id == chat_id).filter(
                    Sentence.word_id is not None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                if len(sentences) > 0:
                    user_db.input_count += 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                else:
                    out = "reached the ending"

            bot.edit_message(chat_id, message_id, out, reply_markup={'inline_keyboard': keyboard_inline_other})
        elif message == 'go left other':
            with Session() as session, session.begin():
                user_db = session.get(User, chat_id)
                current_page = user.input_count - 1
                sentences = session.query(Sentence).filter(Sentence.user_id != chat_id).filter(
                    Sentence.word_id != None).order_by(
                    Sentence.created_at.desc()).offset((current_page - 1) * 10).limit(10).all()

                out = "reached the beginning"
                if current_page > 0:
                    user_db.input_count -= 1
                    session.add(user_db)

                    out = ''
                    for sentence in sentences:
                        out = out + sentence.text + "\n\n"
                elif current_page == 0:
                    user_db.input_count -= 1
                    session.add(user_db)
        else:
            bot.send_message(chat_id, 'please select from commands', reply_markup={'keyboard': [cmd_keyboard]})

    else:
        bot.send_message(chat_id, 'please select from commands', reply_markup={'keyboard': [cmd_keyboard]})
