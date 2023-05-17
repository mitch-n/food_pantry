
import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.buycott.com/upc/07811403")
soup = BeautifulSoup(response.text, features="lxml")

name = soup.find("h2").text
image_div = soup.find("div", {"class": "header_image"})
image = image_div.find("img")["src"]
print(name)
print(image)
