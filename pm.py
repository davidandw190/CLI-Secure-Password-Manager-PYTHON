
import utils.add
import utils.retrieve
import utils.generate
from utils.dbconfig import dbconfig

import argparse
from getpass import getpass
import hashlib
import pyperclip
from rich import print as printc
from pymongo import MongoClient
from bson.objectid import ObjectId

parser = argparse.ArgumentParser(description='Description of the accepted arguments :)')

parser.add_argument('option', help='(a)dd / (e)xtract / (g)enerate')
parser.add_argument("-s", "--name", help="Site name")
parser.add_argument("-u", "--url", help="Site URL")
parser.add_argument("-e", "--email", help="Email")
parser.add_argument("-l", "--login", help="Username")
parser.add_argument("--len", help="Length of the password to generate", type=int)
parser.add_argument("-c", "--copy", action='store_true', help='Copy password to clipboard')

args = parser.parse_args()


def inputAndValidateMasterPassword():
	master_password = getpass("MASTER PASSWORD: ")
	hashed_mp = hashlib.sha256(master_password.encode()).hexdigest()

	# Create database connection
	client = MongoClient("mongodb://localhost:27017/")
	db = client["pm"]
	secrets_collection = db["secrets"]

	# Find the secret document
	secret_document = secrets_collection.find_one()

	if secret_document and hashed_mp == secret_document["masterkey_hash"]:
		return [master_password, secret_document["device_secret"]]
	else:
		printc("[red][!] WRONG! [/red]")
		return None


def main():
	if args.option in ["add", "a"]:
		if args.name is None:
			printc("[red][!][/red] Site Name (-s) required ")
			return
		if args.url is None:
			printc("[red][!][/red] Site URL (-u) required ")
			return
		if args.login is None:
			printc("[red][!][/red] Site Login (-l) required ")
			return

		if args.email is None:
			args.email = ""

		res = inputAndValidateMasterPassword()
		if res is not None:
			utils.add.addEntry(res[0], res[1], args.name, args.url, args.email, args.login)

	if args.option in ["extract", "e"]:
		# if args.name == None and args.url == None and args.email == None and args.login == None:
		# 	# retrieve all
		# 	printc("[red][!][/red] Please enter at least one search field (sitename/url/email/username)")
		# 	return
		res = inputAndValidateMasterPassword()

		search = {}
		if args.name is not None:
			search["sitename"] = args.name
		if args.url is not None:
			search["siteurl"] = args.url
		if args.email is not None:
			search["email"] = args.email
		if args.login is not None:
			search["username"] = args.login

		if res is not None:
			utils.retrieve.retrieveEntries(res[0], res[1], search, decryptPassword=args.copy)

	if args.option in ["generate", "g"]:
		if args.length == None:
			printc("[red][+][/red] Specify length of the password to generate (--length)")
			return
		password = utils.generate.generatePassword(args.length)
		pyperclip.copy(password)
		printc("[green][+][/green] Password generated and copied to clipboard")


main()
