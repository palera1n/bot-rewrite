import mongoengine
from utils.database.user_service import *
from utils.database.guild_service import *


mongoengine.connect('botty', host='localhost', port=27017)
