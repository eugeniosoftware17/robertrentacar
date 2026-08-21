from decouple import config

if config('DB_ENGINE', default='django.db.backends.sqlite3') == 'django.db.backends.mysql':
    import pymysql

    pymysql.version_info = (2, 2, 4, 'final', 0)
    pymysql.install_as_MySQLdb()
