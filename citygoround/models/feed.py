import logging
from google.appengine.ext import db
from django.core.urlresolvers import reverse
from geo.geomodel import GeoModel
from ..utils.slug import slugify
from ..utils.datastore import key_and_entity, normalize_to_key, normalize_to_keys, unique_entities

class FeedReference(db.Model):
    """feed reference models a GTFS Data Exchange entity"""
    
    gtfs_data_exchange_id = db.StringProperty()
    
    # use a float instead of a datetime - otherwise, the locale's timezone shift 
    # is applied when parsing incoming float-based timestamps. This is often
    # applied inconsistently, causing weird problems, so it's best to just avoid
    # it
    date_last_updated = db.FloatProperty() 
    feed_baseurl      = db.LinkProperty()
    name              = db.StringProperty()
    area              = db.StringProperty()
    url               = db.LinkProperty()
    country           = db.StringProperty()
    dataexchange_url  = db.LinkProperty()
    state             = db.StringProperty()
    license_url       = db.LinkProperty()
    date_added        = db.DateTimeProperty()
    is_official       = db.BooleanProperty(default=True)
    
    @staticmethod
    def all_by_most_recent():
        return FeedReference.all().order("-date_added")
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.url)    
    
