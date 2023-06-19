import pyperclip

from rich import print as printc
from rich.console import Console
from rich.table import Table

from utils.add import computeMasterKey
from utils.dbconfig import dbconfig
from utils.encryption import decrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo import MongoClient


def retrieveEntries(master_password, device_secret, search, decryptPassword=False):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pm"]
    entries_collection = db["entries"]

    query = {}
    if len(search) > 0:
        query = search

    results = entries_collection.find(query)

    if entries_collection.count_documents(query) == 0:
        printc("[yellow][-][/yellow] No results for the search")
        client.close()
        return

    if (decryptPassword and entries_collection.count_documents(query) > 1) or (not decryptPassword):
        if decryptPassword:
            printc("[yellow][-][/yellow] More than one result found for the search, therefore not extracting the "
                   "password. \nBe more specific.")

        # for adding a nice header row
        table = Table(title="Results")
        table.add_column("Site Name")
        table.add_column("URL")
        table.add_column("Email")
        table.add_column("Username")
        table.add_column("Password")

        # for adding each record
        for item in results:
            table.add_row(item["sitename"], item["siteurl"], item["email"], item["username"], "{hidden}")

        console = Console()
        console.print(table)
        client.close()
        return

    if decryptPassword and entries_collection.count_documents(query) == 1:
        result = results[0]

        # to compute again the master key
        master_key = computeMasterKey(master_password, device_secret)

        # to decrypt password
        decrypted = decrypt(key=master_key, source=result["password"], keyType="bytes")

        printc("[green][+][/green] Password copied to clipboard")
        pyperclip.copy(decrypted.decode())

    client.close()





