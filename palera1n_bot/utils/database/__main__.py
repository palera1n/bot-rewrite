import mongoengine
from database.user_service import *
from database.guild_service import *


mongoengine.connect('botty', host='localhost', port=27017)
