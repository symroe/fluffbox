import re
import json

import BeautifulSoup
import Flickr.API

from email_parser.models import Mail, Attachment
from fluff.models import Fluff, FluffMedia
from django.conf import settings


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
        # self.mails = Mail.objects.filter(timestamp__gt=last_parse, subject__icontains='Biscuitnews')
        
        for mail in self.mails:
            self.mail = mail
            self.soup = BeautifulSoup.BeautifulSoup(mail.body)
            self.parse()
    
    def sniff_type(self):
        """
        Main parsing function for passing types on to subparsers
        """
        mail_type = None
        body = self.mail.body.split('--')[0]
        body_html = self.mail.body_html.split('--')[0]
        # print self.mail.body
        mail_links = re.findall(r'(http://[^\s]+)', body)
        mail_links.extend(re.findall(r'(http[s]?://[^"|<|>]+)', body_html))

        searches = (
            'flickr',
            'twitter',
            'youtube',
            'audioboo',
        )

        self.links = [m for m in mail_links]

        matches = []
        for m in mail_links:
            mo = re.search("|".join(searches), m)
            if mo:
                matches.append(mo.group(0))
        if matches and matches[0]:

            mail_type = matches[0]
        
        if not mail_type:
            if re.search('http[s]?', body):
                mail_type = 'link'
        
        return mail_type
        
    def parse(self):
        mail_type = self.sniff_type()
        
        # print mail_type
        
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
        
        if new:
            if mail_type == "flickr":
                self.parse_flickr()
            if mail_type == "twitter":
                self.parse_twitter()
            if mail_type == "audioboo":
                self.parse_audioboo()
            if mail_type == "youtube":
                self.parse_youtube()
            if mail_type == "link":
                self.parse_link()
    
    
    def parse_flickr(self):
        main_link = self.links[0]
        
        api = Flickr.API.API(settings.FLICKR_KEY, settings.FLICKR_SECRET)
        
        
        if main_link.endswith('/'):
            main_link = main_link[:-1]
        photo_id = main_link.split('/')[-1]
        
        store_data = {}
        
        rsp = api.execute_method(method='flickr.photos.getInfo', args={'photo_id' : photo_id, 'format' : 'json'})
        data = json.loads(rsp.read()[14:-1])
        if 'photo' in data:
            store_data['farm'] = data['photo']['farm']
            store_data['server'] = data['photo']['server']
            store_data['title'] = data['photo']['title']
            store_data['id'] = data['photo']['id']

        rsp = api.execute_method(method='flickr.photos.getSizes', args={'photo_id' : photo_id, 'format' : 'json'})
        data = json.loads(rsp.read()[14:-1])
        if 'sizes' in data:
            main_link = data['sizes']['size'][3]['source']

        
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.splitlines()[0]
        FM.media_type = 'img'
        FM.url = main_link
        FM.fluff_json = json.dumps(store_data)
        FM.save()
    
    def parse_twitter(self):
        main_link = self.links[0]
        for link in self.links:
            if re.search(r'/status/', link):
                main_link = link
        
        store_data = {}
        store_data['tweet'] = self.mail.body.strip().splitlines()[2]
        store_data['date'] = self.mail.body.strip().splitlines()[1]
        
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'twitter'
        FM.url = main_link
        FM.fluff_json = json.dumps(store_data)
        FM.save()

    def parse_audioboo(self):
        for link in self.links:
            if re.search(r'http://audioboo\.fm/boos/', link):
                main_link = link
        
        embed_html = """
        <object data="http://boos.audioboo.fm/swf/fullsize_player.swf" height="129" id="boo_player_1" type="application/x-shockwave-flash" width="400">
            <param name="movie" value="http://boos.audioboo.fm/swf/fullsize_player.swf" />
            <param name="scale" value="noscale" />
            <param name="salign" value="lt" />
            <param name="bgColor" value="#FFFFFF" />
            <param name="allowScriptAccess" value="always" />
            <param name="wmode" value="window" />
            <param name="FlashVars" value="mp3=%s.mp3" />
            <a href="http://audioboo.fm/boos/246206-i-require-biscuits.mp3?source=embed">Listen!</a
        </object>
        """ % main_link
        
        store_data = {'embed_html' : embed_html}
        
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'audioboo'
        FM.url = main_link
        FM.fluff_json = json.dumps(store_data)
        FM.save()

    def parse_youtube(self):
        main_link = self.links[0]
        for link in self.links:
            if re.search(r'http://youtube\.com', link):
                main_link = link
        
        video_id = re.search(r'watch\?v=([^&]+)', main_link)
        if video_id:
            video_id = video_id.groups(0)[0]
        
        embed_html = """
            <iframe width="480" height="390" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>
        """ % video_id
        
        store_data = {'embed_html' : embed_html}
        
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'youtube'
        FM.url = main_link
        FM.fluff_json = json.dumps(store_data)
        FM.save()
        

    def parse_link(self):
        main_link = self.links[0]
        
        FM = FluffMedia(fluff=self.F)
        FM.title = self.mail.body.strip().splitlines()[0]
        FM.media_type = 'link'
        FM.url = main_link
        FM.save()
        





        




