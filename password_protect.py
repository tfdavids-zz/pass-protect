import os
import sys
import string
import getopt
import sqlite3
import argparse
import getpass
import hashlib
from datetime import datetime

conn = sqlite3.connect("salts.db")
character_set = string.ascii_letters + string.digits + '+$'

def initialize_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS t
                 (account text, username text, salt text, modified text)''')

def create_salt(length=16):
    return "".join([character_set[ord(c) % 64] for c in os.urandom(int(length))])

def store_salt(name, username, salt):
    c = conn.cursor()
    time = str(datetime.now())
    entry = (name, username, salt, time)

    c.execute("INSERT INTO t VALUES (?,?,?,?)", entry)
    conn.commit()

def get_password(name, master_password):
    c = conn.cursor()
    t = (name, )
    c.execute('SELECT salt, username FROM t WHERE account=?', t)
    (salt, username) = c.fetchone()
    return (name, username, ''.join([character_set[ord(c) % 64] for c in hashlib.sha256(salt + '--' + master_password).digest()]))

def delete_password(name):
    c = conn.cursor()
    t = (name, )
    c.execute('DELETE FROM t WHERE account LIKE ?', t)
    conn.commit()

def show_passwords(name):
    c = conn.cursor()
    t = ('%' + name + '%', )
    for row in c.execute('SELECT * FROM t WHERE account LIKE ?', t):
        print "%s (username: %s)" % (row[0], row[1])

def create_password(name, username=None):
    c = conn.cursor()
    salt = create_salt()
    store_salt(name, username, salt)

def print_password(name, master_password):
    (account, username, password) = get_password(name, master_password)
    print "Password for %s" % account
    # print "Username: %s" % username
    print "Password: %s" % password

def password_exists(name):
    c = conn.cursor()
    t = ('%' + name + '%', )
    c.execute('SELECT account FROM t WHERE account LIKE ?', t)
    if c.fetchone():
        return True
    else:
        return False

if __name__ == "__main__":
    initialize_db()

    parser = argparse.ArgumentParser(description='texty text')
    parser.add_argument('name')
    parser.add_argument('-n', '--length', type=int)
    parser.add_argument('-u', '--update', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-l', '--list', dest='lists', action='store_true')
    args = parser.parse_args()

    master_password = getpass.getpass("Please enter your master password: ")

    if args.delete:
        delete_password(args.name)
    elif args.lists:
        show_passwords(args.name)
    elif args.update:
        delete_password(args.name)
        create_password(args.name)
        print_password(args.name, master_password)
    else:
        if not password_exists(args.name):
            create_password(args.name)
        print_password(args.name, master_password)
