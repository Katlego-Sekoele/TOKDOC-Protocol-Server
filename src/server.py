from Utilities import database_manager as database
from RequestHandlers import list as ListRequestHandler
from Utilities import message_parser

database.connect()

# BEGIN SOCKET STUFF
# END SOCKET STUFF

database.disconnect()
