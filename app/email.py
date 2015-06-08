from flask.ext.mail import Message, Mail
from flask import render_template

import app
from app import mail
from app.main.forms import ContactForm


# TODO get these picked up from config object
app.config['MAIL_SUBJECT_PREFIX'] = '[RockyArt]'
app.config['MAIL_SENDER'] = 'RockyArt Admin <admin@rockypardoart.com>'
app.config['MAIL_RECIPIENTS'] = \
    ['mhilema@gmail.com', 'rockypardo.art@gmail.com']
# app.config['MAIL_RECIPIENTS'] = ['mhilema@gmail.com']


def send_email(subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'],
                  recipients=app.config['MAIL_RECIPIENTS'])
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', form=ContactForm(), **kwargs)
    mail.send(msg)
