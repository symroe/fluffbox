import re

import BeautifulSoup

from email_parser.models import Mail, Attachment
from fluff.models import Fluff, FluffMedia


class ParseMail():
    def __init__(self):
        """
        Iterate over all emails received since timestamp
        """
        
        # Get the last fluff where type==mail and only parse since then
        try:
            last_parse = Fluff.objects.filter(fluff_type='mail').latest()
        except:
            # XXX really old date, horrid hack
            last_parse = "1970-01-01"

        self.mails = Mail.objects.filter(timestamp__gt=last_parse)
        
        for mail in self.mails:
            self.mail = mail
            self.soup = BeautifulSoup.BeautifulSoup(mail.body)
            self.parse()
    
    def sniff_type(self):
        """
        Main parsing function for passing types on to subparsers
        """

        # print self.mail.body
        mail_links = re.findall(r'(http://[^\s]+)', self.mail.body)
        mail_links.extend(re.findall(r'(http[s]?://[^"|<|>]+)', self.mail.body_html))

        searches = (
            'flickr',
            'twitter',
            'youtube',
            'audioboo',
        )

        matches = []
        for m in mail_links:
            mo = re.search("|".join(searches), m)
            if mo:
                matches.append(mo.group(0))
        if matches and matches[0]:
            self.links = [m for m in mail_links]
            return matches[0]

    
    def parse(self):
        mail_type = self.sniff_type()
        
        print mail_type
        
        try:
            F = Fluff.objects.get(fluff_id=self.mail.pk)
            new = False
        except Fluff.DoesNotExist:
            F = Fluff(fluff_id=self.mail.pk)
            new = True
        
        F.title = self.mail.subject
        F.timestamp = self.mail.timestamp
        F.save()
        self.F = F
        
        new = True
        if new:
            if mail_type == "flickr":
                self.parse_flickr()
            if mail_type == "twitter":
                self.parse_twitter()
            if mail_type == "audioboo":
                self.parse_audioboo()
    
    
    def parse_flickr(self):
        main_link = self.links[0]
    
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.splitlines()[0]
        FM.media_type = 'img'
        FM.url = main_link
        FM.save()
    
    def parse_twitter(self):
        main_link = self.links[0]
        for link in self.links:
            if re.search(r'/status/', link):
                main_link = link

        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'twitter'
        FM.url = main_link
        FM.save()

    def parse_audioboo(self):
        for link in self.links:
            if re.search(r'http://audioboo\.fm/boos/', link):
                main_link = link
        

        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'audioboo'
        FM.url = main_link
        FM.save()
        












