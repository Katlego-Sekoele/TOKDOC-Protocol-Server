from Utilities import database_manager as database
from RequestHandlers import list as ListRequestHandler

database.connect()

# BEGIN SOCKET STUFF
# END SOCKET STUFF

database.disconnect()
