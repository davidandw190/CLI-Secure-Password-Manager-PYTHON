from getpass import getpass
from crypto.Protocol.KDF import PBKDF2
from crypto.Hash import SHA512
from crypto.Random import get_random_bytes
from rich import print as printc

from utils.dbconfig import dbconfig
from utils.encryption import encrypt


def computeMasterKey(master_password, device_secret):
	password = master_password.encode()  # reminder that `encode()` converts them to bytes
	secret = device_secret.encode()
	key = PBKDF2(password, secret, 32, count=1_000_000, hmac_hash_module=SHA512)
	return key


# def addEntry(master_password, device_secret, sitename, siteurl, email, username):
# 	# to get the new password
# 	password = getpass("PASSWORD: ")
#
# 	master_key = computeMasterKey(master_password, device_secret)
#
# 	encrypted_pass = encrypt(key=master_key, source=password, keyType="bytes")
#
# 	# to add the new entry to the database
# 	db = dbconfig()
# 	cursor = db.cursor()
# 	query = "INSERT INTO pm.entries (sitename, siteurl, email, username, password) values (%s, %s, %s, %s, %s)"
# 	values = (sitename, siteurl, email, username, encrypted_pass)
# 	cursor.execute(query, values)
# 	db.commit()
#
# 	printc("[green][+][/green] New entry added!")

def addEntry(master_password, device_secret, sitename, siteurl, email, username):
	# to get the new password
	password = getpass("PASSWORD: ")

	master_key = computeMasterKey(master_password, device_secret)

	encrypted_pass = encrypt(key=master_key, source=password, keyType="bytes")

	# to add the new entry to the database
	db = dbconfig()
	collection = db["entries"]
	entry = {
		"sitename": sitename,
		"siteurl": siteurl,
		"email": email,
		"username": username,
		"password": encrypted_pass
	}

	collection.insert_one(entry)

	printc("[green][+][/green] New entry added!")
