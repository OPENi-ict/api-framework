# Include the Dropbox SDK
import dropbox
#from dropbox import client, rest, session
from OPENiapp.Providers.baseConnector import basicProvider

from _dbactivity import dbActivity
from _dblocation import dbLocation
from _dbmedia import dbMedia
from _dbproductsServices import dbProductsServices
from _dbprofiles import dbProfiles

class provider(basicProvider, dbActivity, dbLocation, dbMedia, dbProductsServices, dbProfiles):
    """ This class is used to:
        1. Make the connection to the dropbox
    """
    def __init__(self, access_token):#, data):
        """ Initiate the graph and find the OPENi album """
        # Get a DropboxClient object using an existing OAuth 1 access token.
        sess = dropbox.session.DropboxSession(access_token.app.client_id, access_token.app.secret)
        sess.set_token(access_token.token, access_token.token_secret) 
        
        self.connector = dropbox.client.DropboxClient(sess)
        
        