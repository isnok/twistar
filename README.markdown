# twistar with multiple pool support

This is a version of twistar (https://github.com/bmuller/twistar), with support for multiple ConnectionPools.
This way you can use twistar on multiple databases, not only your favourite one :-).

This was made by modifying the `twistar.Registry` class in an way, that most attributes are now kept on instances of the registry, which is now required per custom DBObject-class.

My modified version of the orginal example code:

python ```
#!/usr/bin/env python
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twisted.internet import reactor

# Connect to the first DB
reg_one = Registry(
    adbapi.ConnectionPool(
        'psycopg2',
        host="localhost",
        user="somebody",
        password="secretashell",
        database="test"
    )
)

# ORM classes for the first DB
class OneTable(DBObject):
    REGISTRY = reg_one
    TABLENAME = 'table_one'

# make a new record
r = OneTable(
    data_source = 'twistar-mps',
    data = ['twistar', 'really', 'does', 'a', 'good', 'job']
)

# and save it.
r.save()

# The same for the second DB (it's a mysql DB)

reg_two = Registry(adbapi.ConnectionPool('psycopg2', host="f2-ypsp-bar.infosys.de", user="fraudcheck", password="NoFraudPLZ", database="fraudcheck2"))

class Booking(DBObject):
    REGISTRY = reg3
    TABLENAME = 'booking'


reg2 = Registry(
    adbapi.ConnectionPool(
        'MySQLdb',
        host="localhost",
        user="root",
        db="my_tst"
    )
)

class OtherTable(DBObject):
    REGISTRY = reg_two
    TABLENAME = 'table_two'

s = OtherTable(
    data_foo = 'twistar-mps',
    data = ['twistar', 'really', 'does', 'a', 'good', 'job']
)


# And we can also have multiple DBs of the same kind (here's another postgres)
reg_three = Registry(
    adbapi.ConnectionPool(
        'psycopg2',
        host="remote.host.example.com",
        user="somebody",
        password="secretashell",
        database="readme"
    )
)

class ThirdTable(DBObject):
    REGISTRY = reg_three
    TABLENAME = 'big_big_table'


# do some things in parallel on our dbs:

def done(result):
    print 'Done with result:', result
    reactor.stop()

from twisted.internet.defer import DeferredList

dl = DeferredList([
    OneTable.findBy(data_source='twistar-mps', limit=3),
    s.save(),
    ThirdTable.find(where=['email IS NOT NULL'], limit=1),
]).addCallback(done)

reactor.run()```

