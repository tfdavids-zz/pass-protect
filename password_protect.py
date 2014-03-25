import os
import sys
import string
import getopt

FILE_PATH = "/Users/tdavids/Development/PassProtect/"

def create_password(length=16, leading_letter=False, caps=False, symbol=False):
    characters = string.ascii_letters + string.digits + '+$'
    bytestring = os.urandom(int(length))
    hex_string = "".join([characters[ord(c) % 64] for c in bytestring])
    if leading_letter:
        hex_string = 'a' + hex_string[1:]
    if caps:
        hex_string = 'A' + hex_string[1:]
    if symbol:
        hex_string = hex_string[:-1] + '$'
    return hex_string

def store_password(name, password):
    with open(FILE_PATH + ".passwords.txt", 'a') as password_file:
        password_file.write("%s: %s\n" % (name, password));

def retrieve_passwords(name, master_password):
    results = []
    with open(FILE_PATH + ".passwords.txt", 'r') as password_file:
        for line in password_file:
            if name.lower() in line.lower():
                results.append(line.strip())
    return results

def prompt_options():
    print "Welcome to PassProtect!"
    print "Please enter the number of your option:"
    print "(1) Create a new password."
    print "(2) Retrieve an existing password."
    print "(3) Modify or delete an existing password."
    try:
        choice = int(sys.stdin.readline().strip())
    except KeyboardInterrupt:
        print "\nExiting . . ."
        sys.exit(0)
    if choice == 1:
        create_password()
    elif choice == 2:
        get_password()
    elif choice == 3:
        modify_or_delete_password()

if __name__ == "__main__":
    print "Welcome to PassProtect!"
    print "Please enter the name of the password you would like to create or retrieve:"
    name = sys.stdin.readline().strip()

    results = retrieve_passwords(name)
    if len(results) == 0:
        print "No passwords found."
        print "Create password? Press enter to create password named \"%s\", or Ctrl-C to exit." % name
        print "Optional: to specify options on the password, please type any of the following letters before pressing enter."
        print "'l' if the password must begin with a letter"
        print "'c' if the password must contain a capital letter"
        print "'s' if the password must contain a symbol"
        try:
            options = sys.stdin.readline()
        except KeyboardInterrupt:
            print "\nExiting . . ."
            sys.exit(0)
        leading_letter = 'l' in options
        caps = 'c' in options
        symbol = 's' in options
        password = create_password(leading_letter = leading_letter, caps = caps, symbol = symbol)
        store_password(name, password)
        print "Password successfully created!"
        print "Password for %s is: %s" % (name.strip(), password.strip())
    elif len(results) == 1:
        line = results[0].split(':')
        name, password = line[0], line[1]
    
        print "Password found!"
        print "Password for %s is: %s" % (name.strip(), password.strip())
    else: # len(results) > 1
        print "Multiple passwords found! Please enter the number corresponding to the desired result:"
        for idx, line in enumerate(results):
            full_name = line.split(':')[0].strip()
            print "(%d) %s" % (idx+1, full_name)
        try:
            choice = int(sys.stdin.readline().strip())
        except KeyboardInterrupt:
            print "\nExiting . . ."
            sys.exit(0)
        line = results[choice-1].split(':')
        name, password = line[0], line[1]
    
        print "Password for %s is: %s" % (name.strip(), password.strip())

