
from flask import Flask, render_template
import sqlite3, requests, sys, re
from pprint import pprint
from datetime import datetime
app=Flask(__name__)







@app.route("/")
def hello_world():
	con = sqlite3.connect("../items.db")
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT i.id, i.date, d.name, d.image, COUNT(*) AS quantity FROM items i LEFT JOIN item_details d ON i.id=d.id GROUP BY i.id")
	items = cur.fetchall()
	mod_items = []
	for item in items:
		item = dict(item)
		if  not item["image"] or item["image"].lower() == "not found":
			item["image"] = "static/placeholder.png"
		mod_items.append(item)

	
	return render_template("index.html", items=mod_items)

