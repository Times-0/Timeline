from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

import logging
import os, sys, signal
import json

from twisted.enterprise import adbapi
from twisted.python import log
from twisted.logger import Logger

CONFIG = \
    {
        "MySQL" : {
            'user': 'root',
            'pass': '',
            'dbname': 'timelin',
            'oldname': 'times-cp'
        }
    }

def InitiateColorLogger(name='twisted'):
    from colorlog import ColoredFormatter

    logger = logging.getLogger(name)

    stream = logging.StreamHandler()

    LogFormat = "  %(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"
    stream.setFormatter(ColoredFormatter(LogFormat, log_colors={
        'DEBUG':    'white',
        'INFO':     'cyan',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'black,bg_red',
    }))

    logger.addHandler(stream)
    logger.setLevel(logging.DEBUG)

    logger.info("Porter running")
    return logger


InitiateColorLogger()
logger = Logger()
TEObserver = log.PythonLoggingObserver()
TEObserver.start()

logger.info('DatabasePort running. Initializing values...')

logger.info("Checking existance of module: mysql.connector")
try:
    import mysql.connector
except:
    logger.info("Module mysql.connector not found. Trying to install it")
    
    import pip
    pip.main(['install', 'mysql-connector-python'])
    
    logger.info("Done. Trying to import again.")
    import mysql.connector
    
# get values
logger.debug('Enter MySQL username:')
CONFIG['MySQL']['user'] = raw_input()
logger.debug('Enter MySQL Password:')
CONFIG['MySQL']['pass'] = raw_input()
logger.debug('Enter old MySQL database name (the one from which you are going to port):')
CONFIG['MySQL']['oldname'] = raw_input()
logger.debug('Enter new MySQL database name (the one to which new data is transferred):')
CONFIG['MySQL']['dbname'] = raw_input()

logger.info('Checking DB Name conventions, and rules')

if not CONFIG['MySQL']['dbname'].endswith('line'):
    logger.error('Database name should end with line (eg. Timeline), a strictly enforced nomenclature.')
    sys.exit(0)

logger.info('DB naming rules check - clear')
logger.info('Checking MySQL Credentials')

try:
    MYSQL_CONN = mysql.connector.connect(user=CONFIG['MySQL']['user'], password=CONFIG['MySQL']['pass'], database=CONFIG['MySQL']['oldname'])
except Exception, e:
    print 'Error MySQL', e
    os._exit(1)

@inlineCallbacks
def setupDatabase():
    cursor = MYSQL_CONN.cursor()
    a = cursor.execute("SELECT 1")
    list(cursor)
    
    logger.info("MySQL Connection - good")

    logger.info('Creating database {db}, if not exist', db=CONFIG['MySQL']['dbname'])
    cursor.execute("CREATE DATABASE IF NOT EXISTS `%s`" % (CONFIG['MySQL']['dbname'],))

    logger.info("Connecting to database - {db}", db=CONFIG['MySQL']['dbname'])
    
    cursor.close()
    MYSQL_CONN.close()
    
    MYSQL_CONN.connect(database=CONFIG['MySQL']['dbname'])
    cursor = MYSQL_CONN.cursor()
    
    cursor.execute('SELECT DATABASE();')
    list(cursor)
    
    logger.info("Checking connection to new database...")
    cursor.execute('SELECT 1')
    list(cursor)
    logger.info("Connection status - Good")

    logger.debug("You sure you wanna continue? All data in database - {db} will be wiped.", db=CONFIG['MySQL']['dbname'])
    confirmation = raw_input('Y/n? ')
    if confirmation not in ('Y', 'y'):
        print 'Bye! :~('
        os._exit(1)

    logger.info('Creating tables if not exists')
    import time
    
    oldname = '`{}`'.format(CONFIG['MySQL']['oldname'])
    newname = '`{}`'.format(CONFIG['MySQL']['dbname'])
    
    DBSSQL = open('timeline.sql', 'r')\
        .read().replace("`times-cp`", oldname).replace('`timeline`', newname)
    DBStructureSQL = DBSSQL.split('------- PROCEDURES ------------- ')[0].split(';')
    
    DBProcedureSQL = DBSSQL.split('------- PROCEDURES ------------- ')[1]\
        .split('-- --------------------------------------------------------')
    
    DBSQL = DBStructureSQL + DBProcedureSQL
    
    for sql in DBSQL:
        print 'executing:', sql
        try:
            r = cursor.execute(sql)
        except:
            # try with multi
            try:    
                r = cursor.execute(sql, multi=True)
            except:
                print 'skipping it...'
    
        list(cursor)
    
    cursor.close()
    MYSQL_CONN.close()
    
    MYSQL_CONN.connect(database=CONFIG['MySQL']['dbname'])
    cursor = MYSQL_CONN.cursor()

    logger.info("Done creating tables")
    
    logger.info("Done executing procedures. Ready to port old data set to new one!")
    logger.info("Chilling for a bit...")
    
    
    time.sleep(1)
    logger.info("Commiting to MySQL")
    # bitches stop irking me, this procedure is done once for all
    '''
    logger.info('About to start import old-db set to new one...')

    PROCEDURES = ['IMPORT_INVENTORY_FROM_CP_STRUCT' , 'IMPORT_PENGUIN_FROM_CP_STRUCT', 'IMPORT_ASSETS_FROM_CP_STRUCT',
                  'IMPORT_STAMP_FROM_CP_STRUCT', 'IMPORT_PUFFLE_FROM_CP_STRUCT', 'IMPORT_FRIENDS_FROM_CP_STRUCT']
    for procedure in PROCEDURES:
        logger.info("Executing {prod}", prod=procedure)
        
        stats = cursor.callproc(procedure)
        logger.debug("{prod} - Done", prod=procedure)
        
        print list(stats)
    
    MYSQL_CONN.commit()
    cursor.close()
    
    logger.info("Done...!")
    logger.info("Successfully imported all penguin data from old-db structure.")
    logger.info("At last, importing your igloo likes into new DB Structure.")

    logger.info("Fetching igloo likes...")    
    
    
    cursor = MYSQL_CONN.cursor()
    cursor.execute('SELECT `id`, `likes` FROM `{}`.`igloos` WHERE 1'.format(CONFIG['MySQL']['oldname']))
    
    # [{"count": 1, "id": "{882977da-bf7d-11e7-ac97-a02bb82e593b}", "time": 1545461242}]
    # NULL, igloo id, swid, likes, last like timestamp
    
    logger.info("Fetched igloo likes. Parsing it...")
    LIKE_SQL = []
    
    for (igloo_id, igloo_like_json) in cursor:
        igloo_likes_list = json.loads(igloo_like_json) if igloo_like_json != '' and igloo_like_json is not None else []
        if len(igloo_likes_list) < 1:
            continue

        for like_data in igloo_likes_list:
            LIKE_SQL.append('(NULL, {}, "{}", {}, TIMESTAMP({}))'
                            .format(igloo_id, like_data['id'], like_data['count'], like_data['time']))

    logger.info("Parsed like data. Inserting it into new database...")
    
    if len(LIKE_SQL) > 0:
        LIKE_SQL_RAW = 'INSERT IGNORE INTO `{}`.`igloo_likes` VALUES {};'\
            .format(CONFIG['MySQL']['dbname'], ', '.join(LIKE_SQL))
        print 'executing:', LIKE_SQL_RAW
        r = (cursor.execute(LIKE_SQL_RAW))
    
    MYSQL_CONN.commit()
    cursor.close()
    MYSQL_CONN.close()
    
    logger.info("Done inserting igloo like data.")

    logger.info("One last thing, setting your new db in your Timeline configs, :-D")
    Start_PY = file('./Start.py', 'r+')
    Start_RAW = Start_PY.readlines()
    for i in range(len(Start_RAW)):
        line = Start_RAW[i]
        if not line.startswith('DBMS = DBM'):
            continue

        break  # found, modified, now exit :P

    Start_PY.seek(0)
    Start_PY.truncate()

    Start_RAW[i] = 'DBMS = DBM(user = "{}", passd = "{}", db = "{}")\n'\
        .format(CONFIG['MySQL']['user'], CONFIG['MySQL']['pass'], CONFIG['MySQL']['dbname'])

    Start_PY.write(''.join(Start_RAW))

    Start_PY.close()
    '''
    logger.info("Done :D")

    logger.info("All done, all clear, all set!")
    logger.info("Successfully imported your old `-cp` styled data structure to new one!")
    logger.info("Thank you! Enjoy the new version of timeline!!!")

    print \
    '''
    - Script by dote. Exiting DatabasePort.py
    - BYE ! :~D
    '''

    os._exit(0)

setupDatabase()


reactor.run()
