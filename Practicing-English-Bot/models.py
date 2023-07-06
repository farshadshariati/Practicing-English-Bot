from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz


def current_date_util():
    return datetime.now(tz=pytz.timezone("Asia/Tehran"))


def localize_date_time(date_time: datetime):
    return date_time.replace(tzinfo=pytz.timezone("Asia/Tehran"))


class TimeStamp:
    created_at = Column(TIMESTAMP, default=current_date_util(), nullable=False)
    updated_at = Column(TIMESTAMP, default=current_date_util(), nullable=False)


class User(Base, TimeStamp):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, unique=True)  # chat_id is stored is here
    name = Column(String(128), nullable=True, default=None)
    fname = Column(String(128), nullable=True, default=None)
    status = Column(String(128), nullable=True, default=None)  # any state that the user is currently in like signing up
    input_count = Column(Integer, nullable=True, default=None)  # number of input s of the current state
    current_input = Column(String(256), nullable=True, default=None)
    # relations
    reminder = relationship("Reminder", uselist=False, back_populates='user')
    sentences = relationship("Sentence", back_populates='user')
    words = relationship("Userword", back_populates='user')


class Userword(Base, TimeStamp):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, unique=True)
    word = Column(String(128), nullable=False)
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"))

    # relations
    user = relationship('User', uselist=False, back_populates='words')
    sentence = relationship('Sentence', uselist=False, back_populates='word')


class Reminder(Base, TimeStamp):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"))
    hour = Column(Integer)

    # relations
    user = relationship("User", uselist=False, back_populates='reminder')


class Sentence(Base, TimeStamp):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"))
    subject_id = Column(ForeignKey("subjects.id"), nullable=True)
    word_id = Column(ForeignKey('user_words.id'), nullable=True)
    text = Column(String(512))

    # relations
    user = relationship("User", uselist=False, back_populates='sentences')
    subject = relationship("Subject", uselist=False, back_populates="sentences")
    word = relationship("Userword", uselist=False, back_populates='sentence',primaryjoin="Sentence.word_id==Userword.id")


class Subject(Base, TimeStamp):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String(256), unique=True)

    # relations
    sentences = relationship("Sentence", back_populates="subject")

