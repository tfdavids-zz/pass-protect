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
                 (account text, username text, salt text, length int, modified text)''')

def create_salt(length=16):
    return "".join([character_set[ord(c) % 64] for c in os.urandom(int(length))])

def store_salt(name, username, salt, length):
    c = conn.cursor()
    time = str(datetime.now())
    entry = (name, username if username else 'NULL', salt, length, time)

    c.execute("INSERT INTO t VALUES (?,?,?,?,?)", entry)
    conn.commit()

def get_password(name, master_password):
    c = conn.cursor()
    t = (name, )
    c.execute('SELECT salt, username, length FROM t WHERE account=?', t)
    (salt, username, length) = c.fetchone()
    return (name, username, ''.join([character_set[ord(c) % 64] for c in hashlib.sha256(salt + '--' + master_password).digest()])[:length] )

def delete_password(name):
    c = conn.cursor()
    t = (name, )
    c.execute('DELETE FROM t WHERE account LIKE ?', t)
    conn.commit()

def show_passwords(name):
    c = conn.cursor()
    t = ('%' + name + '%', )
    for row in c.execute('SELECT * FROM t WHERE account LIKE ?', t):
        if row[1] != 'NULL':
            print "%s (username: %s)" % (row[0], row[1])
        else:
            print "%s" % row[0]

def create_password(name, username=None, length=16):
    c = conn.cursor()
    salt = create_salt()
    store_salt(name, username, salt, length)

def print_password(name, master_password):
    (account, username, password) = get_password(name, master_password)
    print "Password for %s" % account
    if username != 'NULL':
        print "Username: %s" % username
    print "Password: %s" % password

def password_exists(name, username):
    c = conn.cursor()
    if not username:
        username = 'NULL'
    t = ('%' + name + '%', username)
    c.execute('SELECT account FROM t WHERE account LIKE ? and username = ?', t)
    if c.fetchone():
        return True
    else:
        return False

if __name__ == "__main__":
    initialize_db()

    parser = argparse.ArgumentParser(description='texty text')
    parser.add_argument('name')
    parser.add_argument('-n', '--length', type=int)
    parser.add_argument('-u', '--username')
    parser.add_argument('-m', '--modify', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-l', '--list', dest='lists', action='store_true')
    args = parser.parse_args()

    # delete a password
    if args.delete:
        try:
            print "Are you sure you want to delete your password named \"%s\"? This can't be undone! Press Enter to continue, or Ctrl-C to exit." % args.name
            sys.stdin.readline()
        except KeyboardInterrupt:
            conn.close()
            sys.exit(0)
        delete_password(args.name)

    # show all passwords
    elif args.lists:
        show_passwords(args.name)

    # modify password
    elif args.modify:
        if not password_exists(args.name, args.username):
            print "Error: couldn't find a password named \"%s\". No action was taken." % args.name
            conn.close()
            sys.exit(0)
        else:
            try:
                print "Are you sure you want to create a new password for \"%s\"? This can't be undone! Press Enter to continue, or Ctrl-C to exit." % args.name
                sys.stdin.readline()
            except KeyboardInterrupt:
                conn.close()
                sys.exit(0)
        delete_password(args.name)
        create_password(args.name)
        master_password = getpass.getpass("Please enter your master password: ")
        print_password(args.name, master_password)

    # create/retrieve password
    else:
        if not password_exists(args.name, args.username):
            try:
                print "No password found. To create a password named \"%s\", type a username (optional), and then press enter." % args.name
                sys.stdin.readline()
            except KeyboardInterrupt:
                conn.close()
                sys.exit(0)
            if args.length:
                create_password(args.name, args.username, args.length)
            else:
                create_password(args.name, args.username)
        master_password = getpass.getpass("Please enter your master password: ")
        print_password(args.name, master_password)
    conn.close()
