scan_queue = "/home/pi/food_pantry/scan_queue.txt"

while True:
	upc = input(">> ")
	with open (scan_queue, 'a') as f:
		f.write(f"{upc}\n")

