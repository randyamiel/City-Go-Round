from uuid import uuid4

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images


class ImageBlob(db.Model):
    ORIGINAL_SIZE = (0, 0)
    
    # Image entities are unique across family+width+height
    # All images with the same "family" have the same effective image, but may have different width/height        
    image = db.BlobProperty() # DEPRECATED -- images will be served from the blobstore...
    blob = blobstore.BlobReferenceProperty()
    family = db.StringProperty(required = True, indexed = True)
    width = db.IntegerProperty(indexed = True)
    height = db.IntegerProperty(indexed = True)
    extension = db.StringProperty()

    @staticmethod
    def new_with_unique_family():
        return ImageBlob(family = str(uuid4()).replace('-', ''))
    
    @staticmethod
    def all_in_family(family):
        return ImageBlob.all().filter('family =', family)
        
    @staticmethod
    def get_for_family_and_size(family, (width, height)):
        return ImageBlob.all().filter('family =', family).filter('width =', width).filter('height =', height).get()

    @staticmethod
    def get_original_for_family(family):
        return ImageBlob.get_for_family_and_size(family, ImageBlob.ORIGINAL_SIZE)

    # DEPRECATED
    @staticmethod
    def get_bytes_and_extension_for_family_and_size(family, (width, height)):
        blob = ImageBlob.get_for_family_and_size(family, (width, height))
        if not blob: return (None, None)
        return (blob.image, blob.extension)

    def __str__(self):
        return "%s (%dx%d)" % (self.family, self.width, self.height)    
    