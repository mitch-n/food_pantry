import sqlite3, requests, sys, re, time
from pprint import pprint
from datetime import datetime
from bs4 import BeautifulSoup
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

RST = None     # on the PiOLED this pin isnt used
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()

image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/home/pi/food_pantry/Pixellari.ttf', 16)

padding = 0
top = padding
bottom = disp.height-padding
x = 0

def write(top_text="", bottom_text=""):
	draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
	draw.text((x, top), top_text,  font=font, fill=255)
	draw.text((x, top+15), bottom_text,  font=font, fill=255)
	disp.image(image)
	disp.display()

scan_queue="/home/pi/food_pantry/scan_queue.txt"
db_location="/home/pi/food_pantry/items.db"

con = sqlite3.connect(db_location)
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
	
	name = None
	description = None
	cost = None
	image = None
	
	#Search upcitemdb
	print("Searching upcitemdb")
	response = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc}")
	if response.status_code == 200 and response.json()["total"]>0:
		print("Item found in upcitemdb")
		item_found=True
		item = response.json()["items"][0]

		name = item["title"] if not name else name
		description = item["description"] if not description else description
		
		try:
			cost = response.json()["offers"][0]["price"] if not cost else cost
		except Exception:
			pass
		
		try:
			image = item["images"][0] if not image else image
		except Exception:
			pass
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
	print("Searching Buycott")
	response = requests.get(f"https://www.buycott.com/upc/{upc}")
	if response.status_code == 200:
		print("Item found in Buycott")
		soup = BeautifulSoup(response.text)

		name = soup.find("h2").text if not name else name
		image_div = soup.find("div", {"class": "header_image"})
		image = image_div.find("img")["src"] if not image else image
	else:
		print("Item not found in Buycott")
	
	#Search Barcode Report
	print("Searching Barcode Report")
	response = requests.get(f"https://barcodereport.com/{upc}")
	if response.status_code == 200:
		print("Item found in Barcode Report")
		try:
			match = re.search("<h1[^>]+>(?P<name>[^<]+)",response.text)
			name = match.groups("name")[0] if not name else name
		except:
			print("Name not found in Barcode Report")

	else:
		print("Item not found in Barcode Report")
	
	
	cur.execute("INSERT INTO item_details VALUES(?, ?, ?, ?, ?)", (upc, name if name else "Not Found", description if description else "Not Found", cost if cost else "Not Found", image if image else "Not Found"))
	con.commit()
	
	return

def add_item(upc):
	cur.execute("INSERT INTO items VALUES(?, ?)", (upc, datetime.now()))
	con.commit()
	
	print(upc)
	
	# Check for details
	res = cur.execute("SELECT id FROM item_details WHERE id=?", [upc])
	if not res.fetchone():
		print("Item details not found")
		get_item_details(upc)
	print(f"Added {upc}")
		
def remove_item(upc):
	cur.execute("""DELETE FROM items WHERE id=? and date IN (SELECT date FROM items WHERE id=? ORDER BY date ASC LIMIT 1);""", [upc, upc])
	con.commit()
	print(f"Deleted oldest record for {upc}")

mode = "ADD"
print(f"Mode: {mode}")
print("Ready to Scan")
write(f"Mode: {mode}", "Scanner Ready")

start_time = datetime.now()
cur_count = 1
cur_upc = 0

while True:
	with open(scan_queue, "r+") as f:
		print("OPENED FILE")
		for upc in f.readlines():
			start_time = datetime.now()
			upc = upc.strip()
			print(upc)

			if upc != cur_upc:
				cur_count = 1
				cur_upc = upc
			else:
				cur_count += 1

			if upc == "00000000":
				mode = "REMOVE"
				print("Set mode to REMOVE")
			elif upc == "11111115":
				mode = "ADD"
				print("Set mode to ADD")
			else:
				if mode == "ADD":
					add_item(upc)
				elif mode == "REMOVE":
					remove_item(upc)
	
				res = cur.execute("SELECT COUNT(*) AS quantity FROM items WHERE id=?", [upc])
				#item = dict(res.fetchone())
				item = res.fetchone()
				write(f"{upc}", f"Scanned Ct: {cur_count}")
				# time.sleep(.2)
		f.seek(0)
		f.write("")
		f.truncate()

	duration = datetime.now() - start_time
	if duration.seconds > 60:
		write()
	elif duration.seconds > 10:
		write(f"Mode: {mode}", "")
	time.sleep(.2)
	
	
	
	
	
	


