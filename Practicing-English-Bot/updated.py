import logging
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up persistence (optional)
persistence = PicklePersistence(filename='bot_data.pickle')

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi there! Use /help to see what I can do.')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Here are some things I can do:\n\n'
        '/edit_csv - Edit a CSV file\n'
        '/add_subject - Add a new subject to a list\n'
        '/delete_subject - Delete a subject from a list\n'
        '/change_info - Change user information\n')

def edit_csv(update: Update, context: CallbackContext) -> None:
    """Edit a CSV file."""
    # Check if a file was sent
    if not update.message.document:
        update.message.reply_text('Please send me a CSV file.')
        return
    
    # Get the file ID and download the file
    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)
    
    # Save the file to disk
    filename = os.path.join('csv_files', file_id + '.csv')
    file.download(custom_path=filename)
    
    update.message.reply_text(f'File "{file.file_name}" saved.')

def add_subject(update: Update, context: CallbackContext) -> None:
    """Add a new subject to a list."""
    # Check if a subject was sent
    if not update.message.text:
        update.message.reply_text('Please send me the name of a subject.')
        return
    
    # Get the subject and chat ID
    subject = update.message.text
    chat_id = update.effective_chat.id
    
    # Load the list of subjects from persistent storage (optional)
    subjects = context.user_data.get('subjects', {})
    
    # Add the subject to the list
    if chat_id in subjects:
        subjects[chat_id].append(subject)
    else:
        subjects[chat_id] = [subject]
    
    # Save the list of subjects to persistent storage (optional)
    context.user_data['subjects'] = subjects
    
    update.message.reply_text(f'Subject "{subject}" added to your list.')

def delete_subject(update: Update, context: CallbackContext) -> None:
    """Delete a subject from a list."""
    # Check if a subject was sent
    if not update.message.text:
        update.message.reply_text('Please send me the name of a subject.')
        return
    
    # Get the subject and chat ID
    subject = update.message.text
    chat_id = update.effective_chat.id
    
    # Load the list of subjects from persistent storage (optional)
    subjects = context.user_data.get('subjects', {})
    
    # Remove the subject from the list
    if chat_id in subjects and subject in subjects[chat_id]:
        subjects[chat_id].remove(subject)
        update.message.reply_text(f'Subject "{subject}" removed from your list.')
    else:
        update.message.reply_text(f'Subject "{subject}" not found in your list.')

    # Save the list of subjects to persistent storage (optional)
    context.user_data['subjects'] = subjects

def change_info(update: Update, context: CallbackContext) -> None:
    """Change user information."""
    # Get the chat ID
    chat_id = update.effective_chat.id
    
    # Load the user information from persistent storage (optional)
    info = context.user_data.get('info', {})
    
    # Check if any updates were sent
    if not update.message.text:
        # Send the current information
        if chat_id in info:
            update.message.reply_text(f'Your information is:\n\n{info[chat_id]}')
        else:
            update.message.reply_text('You have no information saved.')
    else:
        # Update the user information
        info[chat_id] = update.message.text
        
        update.message.reply
