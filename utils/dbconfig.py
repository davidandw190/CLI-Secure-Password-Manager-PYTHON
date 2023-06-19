import mysql.connector
from rich.console import Console
from pymongo import MongoClient
from bson.objectid import ObjectId


console = Console()


def dbconfig():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["pm"]
    except Exception as e:
        console.print_exception(show_locals=True)
        return

    return db






