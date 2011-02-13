import sys
import re
import datetime
import time
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile

from email_parser.models import Mail, Attachment


class Command(BaseCommand):
    
    def handle(self, **options):
        
        def decodeUnknown(charset, string):
            if not charset:
                try:
                    return string.decode('utf-8')
                except:
                    return string.decode('iso8859-1')
            return unicode(string, charset)
        
        
        def decode_mail_headers(string):
            decoded = decode_header(string)
            return u' '.join([unicode(msg, charset or 'utf-8') for msg, charset in decoded])
        
        
        try:
            
            M = imaplib.IMAP4_SSL("imap.gmail.com")
            M.login("sxswbellybutton","rewiredstate")
            M.select("INBOX")
            typ, data = M.SEARCH(None, 'ALL')
            msgnums = data[0].split()
            for num in msgnums:
                status, data =  M.FETCH(num, '(RFC822)')
                message = email.message_from_string(data[0][1])
                subject = message.get('subject', '[no subject]')
                subject = decode_mail_headers(decodeUnknown(message.get_charset(), subject))
                
                message_id = message.get('message-id')
                message_id = re.sub("<|>|@", "", message_id)
                

                timestamp = time.mktime(parsedate(message.get('date')))
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                                
                msg_from = message.get('from')
                files = []
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue

                    name = part.get_param("name")
                    if name:
                        name = name

                    if part.get_content_maintype() == 'text' and name == None:
                        if part.get_content_subtype() == 'plain':
                            body_plain = decodeUnknown(part.get_content_charset(), part.get_payload(decode=True))
                        else:
                            body_html = part.get_payload()
                    else:
                        if not name:
                            ext = mimetypes.guess_extension(part.get_content_type())
                            name = "part-%i%s" % (counter, ext)
                            
                        filename = "%s--%s" % (message_id, name,)
                        files.append({
                            'filename': filename,
                            'content': part.get_payload(decode=True),
                            'type': part.get_content_type()},
                            )


                if body_plain:
                    body = body_plain
                else:
                    body = _('No plain-text email body available. Please see attachment email_html_body.html.')
                
                try:
                    F = Mail.objects.get(pk=message_id)
                except:
                    F = Mail(pk=message_id)
                
                F.subject = subject
                F.msg_from = msg_from
                F.timestamp = timestamp
                F.body = body
                F.body_html = body_html
                F.save()

                for f in files:
                    cf = ContentFile(f['content'])
                    try:
                        A = Attachment.objects.get(name=f['filename'], mail=F)                        
                    except Exception, e:
                        A = Attachment(name=f['filename'], mail=F)
                        A.filename.save(f['filename'], cf)
                        A.save()
            M.close()
            M.logout()
        except KeyboardInterrupt:
            M.close()
            M.logout()
            
            import sys
            sys.exit()