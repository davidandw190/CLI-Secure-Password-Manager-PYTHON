from pymongo import MongoClient
from bson.objectid import ObjectId

import os
import sys
import string
import random
import hashlib
import sys
from getpass import getpass

from utils.dbconfig import dbconfig
from pymongo import MongoClient
from bson.objectid import ObjectId


from rich import print as printc
from rich.console import Console

console = Console()


def checkConfig():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pm"]

    collections = db.list_collection_names()
    if "secrets" in collections and "entries" in collections:
        return True
    return False


def generateDeviceSecret(length=10):
    characters = string.ascii_uppercase + string.digits
    device_secret = ''.join(random.choices(characters, k=length))
    return device_secret


def make():
    if checkConfig():
        printc("[red][!] Already Configured! [/red]")
        return

    printc("[green][+] Creating new config [/green]")

    # to create the database connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pm"]

    # to create the secrets collection
    secrets_collection = db["secrets"]
    secrets_collection.create_index("masterkey_hash", unique=True)

    # to create the entries collection
    entries_collection = db["entries"]
    entries_collection.create_index("sitename", unique=True)

    master_password = ""
    printc("[green][?] First of all, let me tell you what a [bold]MASTER PASSWORD[/bold] is..\n\n"
           "A [bold]MASTER PASSWORD[/bold] is the only password you will need to remember in order to access all your "
           "other passwords. Choosing a strong [bold]MASTER PASSWORD[/bold] is essential because all your other passwor"
           "device_secret will be [bold]encrypted[/bold] with a key that is derived from your [bold]MASTER PASSWORD[/bold].\n\n"
           "Therefore, please choose a strong one that has upper and lower case characters, numbers and also special "
           "characters. Remember your [bold]MASTER PASSWORD[/bold] because it won't be stored anywhere by this program,"
           " and you also cannot change it once chosen. [/green]\n")

    while True:
        master_password = getpass("Choose a MASTER PASSWORD: ")
        if master_password == getpass("Re-type: ") and master_password != "":
            break
        printc("[yellow][-] Please try again.[/yellow]")

    # to hash the MASTER PASSWORD
    hashed_master_password = hashlib.sha256(master_password.encode()).hexdigest()
    printc("[green][+][/green] Generated hash of MASTER PASSWORD")

    # to generate a device secret
    device_secret = generateDeviceSecret()
    printc("[green][+][/green] Device Secret generated!")

    # to add them to the secrets collection
    secret_data = {
        "masterkey_hash": hashed_master_password,
        "device_secret": device_secret
    }

    secrets_collection.insert_one(secret_data)

    printc("[green][+][/green] Added to the database")

    printc("[green][+] Configuration done![/green]")

    client.close()


def delete():
    printc("[red][!] Deleting a config clears the device secret and all your entries from the database.\n\n "
           "This means you will lose access to all your passwords that you have added into the password manager until "
           "now. Only do this if you truly want to [bold]'DESTROY'[/bold] all your entries. \n\n"
           "!! This action cannot be undone. !! [/red]")

    while True:
        op = input("So are you sure you want to continue? (y/N): ")
        if op.upper() == "Y":
            break
        if op.upper() == "N" or op.upper == "":
            sys.exit(0)
        else:
            continue

    printc("[green][-][/green] Deleting config")

    if not checkConfig():
        printc("[yellow][-][/yellow] No configuration exists to delete, you maniac!")
        return

    # to create database connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pm"]

    # to drop the database
    client.drop_database("pm")
    printc("[green][+] Config deleted![/green]")

    client.close()


def remake():
    printc("[green][+][/green] Remaking config..")
    delete()
    make()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python config.py <make/delete/remake>")
        sys.exit(0)

    if sys.argv[1] == "make":
        make()
    elif sys.argv[1] == "delete":
        delete()
    elif sys.argv[1] == "remake":
        remake()
    else:
        printc("[yellow][?][/yellow] Usage: python config.py <make/delete/remake>")
