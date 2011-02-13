import datetime
import json
from django.db import models

class FluffMedia(models.Model):
    media_type = models.CharField(blank=True, max_length=100)
    url = models.URLField(blank=True, verify_exists=True)
    title = models.CharField(blank=True, max_length=255)
    fluff = models.ForeignKey('Fluff')
    
    
    def as_json(self):
        obj = {
            'title' : self.title,
            'url' : self.url,
            'media_type' : self.media_type,
        }
        return obj

class Fluff(models.Model):
    fluff_id = models.CharField(blank=True, max_length=255)
    title = models.CharField(blank=True, max_length=255)
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    fluff_type = models.CharField(blank=True, max_length=100)
    
    class Meta:
        get_latest_by = 'timestamp'
    
    
    def as_json(self):
        obj = {
            'title' : self.title,
            'timestamp' : str(self.timestamp),
            'type' : self.fluff_type,
            'assets' : [m.as_json() for m in self.fluffmedia_set.all()]
        }

        return obj