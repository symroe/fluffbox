import sys
import re
import imaplib
import email
from email.header import decode_header

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

from fluff import fluff_parsers
from fluff.models import Fluff, FluffMedia

class Command(BaseCommand):
    
    def handle(self, **options):
        
        fluff_parsers.ParseMail()