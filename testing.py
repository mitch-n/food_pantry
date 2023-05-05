import requests
upc = "681131077460"
data = f"action=bs_ajax_sku_finder_get_results&ajax_security=387228f9b1&search={upc}&store_type=3&MlEToKhxkPavV=bu83WjvNH[QmI&Rq-vkNOg=OA5VPaEM&-HjcPlxfDAru=OelfsJ7_iXka"

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0", 
"Accept": "*/*", 
"Accept-Language": "en-US,en;q=0.5", 
"Accept-Encoding": "gzip, deflate, br"
}

response = requests.post(f"https://brickseek.com/wp-admin/admin-ajax.php",data=data)

print(response)
print(response.text)
