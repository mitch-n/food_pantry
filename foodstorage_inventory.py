import sqlite3, requests, sys, re
from pprint import pprint
from datetime import datetime

con = sqlite3.connect("items.db")
cur = con.cursor()

# Create Items database
try:
	cur.execute("CREATE TABLE items(id, date)")
	print("Created ITEMS Database")
except sqlite3.OperationalError as e:
	if e.__str__() == "table items already exists":
		print("ITEMS Database Found")
	else:
		print("Error: Quitting")
		sys.exit()

# Create Item_Details database
try:
	cur.execute("CREATE TABLE item_details (id, name, description, cost, image)")
	print("Created ITEM_DETAILS Database")
except sqlite3.OperationalError as e:
	if e.__str__() == "table item_details already exists":
		print("ITEM_DETAILS Database Found")
	else:
		print("Error: Quitting")
		sys.exit()


def get_item_details(upc):
	#Search upcitemdb
	print("Searching upcitemdb")
	response = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc}")
	if response.status_code == 200 and response.json()["total"]>0:
		print("Item found in upcitemdb")
		item_found=True
		
		item = response.json()["items"][0]
		
		try:
			cost = response.json()["offers"][0]["price"]
		except Exception:
			cost = "Not Found"
		
		try:
			image = item["images"][0]
		except Exception:
			image = "Not Found"
		
		cur.execute("INSERT INTO item_details VALUES(?, ?, ?, ?, ?)", (upc, item["title"], item["description"], cost, image))
		con.commit()
		print("Item loaded into item_details")
		return
	else:
		print("Item not found in upcitemdb")
		
	#Search BRICKSEEK	
	"""
	print("Searching BRICKSEEK")
	response = requests.get(f"https://brickseek.com/wp-admin/admin-ajax.php")
	
	action=bs_ajax_sku_finder_get_results
	&ajax_security=387228f9b1
	&search=681131077460
	&store_type=3
	&MlEToKhxkPavV=bu83WjvNH[QmI&Rq-vkNOg=OA5VPaEM&-HjcPlxfDAru=OelfsJ7_iXka
	"""
	
	#Search buycott (Scraping)
	"""
	print("Searching buycott")
	url = "https://www.buycott.com/upc/07811403"
	"""
	
	#Search Barcode Report
	print("Searching Barcode Report")
	response = requests.get(f"https://barcodereport.com/{upc}")
	if response.status_code == 200:
		print("Item found in Barcode Report")
		try:
			match = re.search("<h1[^>]+>(?P<title>[^<]+)",response.text)
			title = match.groups("title")[0]
		except:
			print("Title not found in Barcode Report")
			return
		cur.execute("INSERT INTO item_details VALUES(?, ?, ?, ?, ?)", (upc, title, "Not Found", "Not Found", "Not Found"))
		con.commit()
		print("Item loaded into item_details")
		return
	else:
		print("Item not found in Barcode Report")
	
	
	return
		
print("Ready to Scan")
while True:
	upc = input(">> ")
	cur.execute("INSERT INTO items VALUES(?, ?)", (upc, datetime.now()))
	con.commit()
	
	print(upc)
	
	# Check for details
	res = cur.execute("SELECT id FROM item_details WHERE id=?", [upc])
	if not res.fetchone():
		print("Item details not found")
		get_item_details(upc)
	
	
	
	
	
	
	
	


