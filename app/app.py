from flask import Flask, render_template, request
import sqlite3, requests, sys, re
from pprint import pprint
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

app=Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

database_location = "/home/pi/food_pantry/items.db"

@app.route("/")
def home():
	con = sqlite3.connect(database_location)
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT i.id, i.date, d.name, d.image, COUNT(*) AS quantity FROM items i LEFT JOIN item_details d ON i.id=d.id WHERE LENGTH(i.id)>1 GROUP BY i.id")
	items = cur.fetchall()
	mod_items = []
	for item in items:
		item = dict(item)
		if  not item["image"] or item["image"].lower() == "not found":
			item["image"] = "static/placeholder.png"
		mod_items.append(item)

	
	return render_template("index.html", items=mod_items)
	
@app.route("/api/modify_item", methods=["POST"])
def modify_item():
	# UPC, Field, Value
	print(request)
	try:
		data = request.get_json()
		print(data)
		con = sqlite3.connect(database_location)
		cur = con.cursor()
		if data["field"] == "name":
			cur.execute("UPDATE item_details SET name = ? WHERE id=?", [data["value"], data["upc"]])
		elif data["field"] == "image":
			cur.execute("UPDATE item_details SET image = ? WHERE id=?", [data["value"], data["upc"]])
		elif data["field"] == "qty":
			pass
		con.commit()
		return {"message":"success"}
	except Exception as e:
		return {"message": e}

@app.route("/api/delete_item", methods=["POST"])
def delete_item():
	try:
		data = request.get_json()
		con = sqlite3.connect(database_location)
		cur = con.cursor()
		cur.execute("DELETE FROM items WHERE id=?", [data["upc"]])
		con.commit()
		return {"message":"success"}
	except Exception as e:
		return {"message": e}
		
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)

		
	



