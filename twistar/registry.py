"""
Module handling global registration of variables and classes.
"""

from twisted.python import reflect

#from BermiInflector.Inflector import Inflector

from twistar.exceptions import ClassNotRegisteredError

registries = {}

class Registry:
    """
    A data store containing mostly class variables that act as constants.

    @var DBPOOL: This should be set to the C{twisted.enterprise.dbapi.ConnectionPool} to
    use for all database interaction.
    """
    REGISTRATION = {}

    def __init__(self, DBPOOL):
        self.SCHEMAS = {}
        self.IMPL = None
        self.DBPOOL = DBPOOL


    @classmethod
    def register(self, *klasses):
        """
        Register some number of classes in the registy.  This is necessary so that when objects
        are created on the fly (specifically, as a result of relationship C{get}s) the package
        knows how to find them.

        @param klasses: Any number of parameters, each of which is a class.
        """
        for klass in klasses:
            Registry.REGISTRATION[klass.__name__] = klass


    def getClass(self, name):
        """
        Get a registered class by the given name.
        """
        if not Registry.REGISTRATION.has_key(name):
            raise ClassNotRegisteredError, "You never registered the class named %s" % name
        return Registry.REGISTRATION[name]


    def getDBAPIClass(self, name):
        """
        Per U{http://www.python.org/dev/peps/pep-0249/} each DBAPI driver must implement it's
        own Date/Time/Timestamp/etc classes.  This method provides a generalized way to get them
        from whatever DB driver is being used.
        """
        driver = self.DBPOOL.dbapi.__name__
        path = "%s.%s" % (driver, name)
        return reflect.namedAny(path)


    def getConfig(self):
        """
        Get the current DB config object being used for DB interaction.  This is one of the classes
        that extends L{base.InteractionBase}.
        """
        if self.IMPL is not None:
            return self.IMPL

        if self.DBPOOL is None:
            msg = "You must set Registry().DBPOOL to a adbapi.ConnectionPool before calling this method."
            raise RuntimeError, msg
        dbapi = self.DBPOOL.dbapi
        if dbapi.__name__ == "MySQLdb":
            from twistar.dbconfig.mysql import MySQLDBConfig
            self.IMPL = MySQLDBConfig(self)
        elif dbapi.__name__ == "sqlite3":
            from twistar.dbconfig.sqlite import SQLiteDBConfig
            self.IMPL = SQLiteDBConfig(self)
        elif dbapi.__name__ == "psycopg2":
            from twistar.dbconfig.postgres import PostgreSQLDBConfig
            self.IMPL = PostgreSQLDBConfig(self)
        elif dbapi.__name__ == "pyodbc":
            from twistar.dbconfig.pyodbc import PyODBCDBConfig
            self.IMPL = PyODBCDBConfig(self)
        else:
            raise NotImplementedError, "twisteddb does not support the %s driver" % dbapi.__name__

        return self.IMPL
