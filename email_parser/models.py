import datetime
from django.db import models

"""
Stores emails parsed form email_parser
"""

class Attachment(models.Model):
    name = models.CharField(blank=True, max_length=255)
    filename = models.FileField(upload_to='attachments')
    mail = models.ForeignKey('Mail')

class Mail(models.Model):
    msg_id = models.CharField(blank=True, max_length=255, primary_key=True)
    msg_from = models.CharField(blank=True, max_length=255)
    subject = models.CharField(blank=True, max_length=255)
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    body = models.TextField(blank=True)
    body_html = models.TextField(blank=True)

