import pymongo
import logging
import config
import urllib.error, urllib .request

class Database:
    """ Database Singleton class """

    class __impl:
        """ Implementation of the database class """

        def __init__(self):
            mongo_client = pymongo.MongoClient(config.DATABASE_CONFIG['database_url'])
            self.db = mongo_client[config.DATABASE_CONFIG['database_name']]

        def get_collection(self, collection):
            """ Returns a reference to a collection identified by name

            Arguments:
                collection {string} -- the collection name on the database

            Returns:
                [pymongo.collection.Collection] -- [collection reference for API usage]
            """
            return self.db[collection]

    # The private class attribute holding the "one and only instance"
    __instance = __impl()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class ServerPublisher:

    def __init__(self, server_name, endpoint, logger):
        self.endpoint = endpoint
        self.server_name = server_name
        self.server_short_name = self.server_name.split('_')[0]
        self.name = self.__class__.__name__
        self.logger = logger

        database = Database()
        self.collection = database.get_collection(config.DATABASE_CONFIG['database_collection'])

    def check_connection(self):
        try:
            urllib.request.urlopen(url=config.DATABASE_CONFIG['check_connection_address'],
                                   timeout=config.DATABASE_CONFIG['check_connection_timeout'])
            return True
        except urllib.error.URLError:
            return False


    def publish(self):
        """
        Publish the OPCUA Server information to mLab
        """
        result = None
        try:
            result = self.collection.find_one({'name': self.server_short_name})
        except:
            self.logger.info("Cannot connect to the DB. Check the connection.")
            return result


        if result is None:
            result = self.collection.insert_one({'endpoint': self.endpoint, 'name': self.server_short_name})
            self.logger.info("OPCUA Server %s has been included: %s ", self.server_name, self.endpoint)
        else:
            result = self.collection.find_and_modify(
                {'name': self.name},
                {'endpoint': self.endpoint, 'name': self.name})
            self.logger.info("OPCUA Server %s has been updated: %s ", self.server_name, self.endpoint)
        return result
