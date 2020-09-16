import requests,fake_useragent
from bs4 import BeautifulSoup
import time

ua=fake_useragent.UserAgent()

# def extract_url(url):
#     if url.find("www.amazon.in") != -1:
#         index = url.find("/dp/")
#         if index != -1:
#             index2 = index + 14
#             url = "https://www.amazon.in" + url[index:index2]
#         else:
#             index = url.find("/gp/")
#             if index != -1:
#                 index2 = index + 22
#                 url = "https://www.amazon.in" + url[index:index2]
#             else:
#                 url = None
#     else:
#         url = None
#     return url

def price_2_num(p):
    temp_price=''
    for i in p.text:
        if i.isdigit() or i=='.':
            temp_price+=i
    return temp_price

def get_product_info_flipkart(url):
	try:
		r=requests.get(url,headers={"User-Agent":str(ua.chrome)})   
	except requests.exceptions.TooManyRedirects:
		time.sleep(10)
		r=requests.get(url,headers={"User-Agent":str(ua.chrome)})

	soup=BeautifulSoup(r.text,'html.parser')
	
	# Price of the product 
	price=soup.find_all('div',{"class":"_1vC4OE _3qQ9m1"})
	price_in_num=price_2_num(price[0])
	
	# Name of the product
	product_name=soup.find_all('span',{"class":"_35KyD6"})[0].get_text(strip=True)
	
	# Stock status of the product
	sold_out="Yes"
	sold_out_temp=soup.find_all('div',{"class":"_9-sL7L"})
	if sold_out_temp:
		sold_out="No"
	
	return {"name":product_name,"price_with_currency":price[0].text,"price_in_num":float(price_in_num),"availability":sold_out}


# def get_product_info_amazon(url):
# 	headers = {
#         'authority': 'www.amazon.com',
#         'pragma': 'no-cache',
#         'cache-control': 'no-cache',
#         'dnt': '1',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'sec-fetch-site': 'none',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-dest': 'document',
#         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#     }
# 	r=requests.get(url,headers=headers)   
# 	soup=BeautifulSoup(r.content,'html.parser')
# 	print(r.content)
# 	# Get product_name
# 	# product_name=soup.find_all('span',{"class":"a-size-large product-title-word-break"})[0].get_text(strip=True)
# 	# print(product_name)

# 	#price of the product
# 	price=price_2_num(soup.find_all('span',{'class':"a-size-medium a-color-price priceBlockBuyingPriceString"})[0])
# 	print(float(price))


# extracted_url=extract_url("https://www.amazon.in/Acer-AN515-54-15-6-inch-i5-9300H-processor/dp/B0894NY25W/ref=sr_1_1?dchild=1&keywords=acer+nitro+5&qid=1599319002&sr=8-1")
# if extracted_url:
# 	print(extracted_url)
# 	get_product_info_amazon(extracted_url)

# print(get_product_info_flipkart("https://www.flipkart.com/acer-nitro-5-ryzen-quad-core-8-gb-1-tb-hdd-windows-10-home-4-gb-graphics-amd-radeon-rx-560x-an515-43-gaming-laptop/p/itmfgnhgs9tjsfzf?pid=COMFGNHG2CKKGH7Z&lid=LSTCOMFGNHG2CKKGH7ZM3XRSF&marketplace=FLIPKART&srno=s_1_5&otracker=AS_Query_HistoryAutoSuggest_1_1_na_na_na&otracker1=AS_Query_HistoryAutoSuggest_1_1_na_na_na&fm=SEARCH&iid=9a592074-a132-4d3d-95da-c8ff6cbb74d3.COMFGNHG2CKKGH7Z.SEARCH&ppt=sp&ppn=sp&ssid=w098q60gghgi64u81599219943547&qH=6a476f61ea33f248"))

# print(get_product_info_flipkart("https://www.flipkart.com/acer-nitro-5-core-i5-9th-gen-8-gb-1-tb-hdd-windows-10-home-3-gb-graphics-nvidia-geforce-gtx-1050-an515-54-563y-an515-54-52h2-gaming-laptop/p/itmcc400f97b66f1?pid=COMFHNY8HYPHY7ZH&lid=LSTCOMFHNY8HYPHY7ZHIIO4JI&marketplace=FLIPKART&srno=s_1_1&otracker=AS_Query_HistoryAutoSuggest_1_1_na_na_na&otracker1=AS_Query_HistoryAutoSuggest_1_1_na_na_na&fm=organic&iid=7f2b4a1e-d376-4099-a3f1-1010bd6013bc.COMFHNY8HYPHY7ZH.SEARCH&ssid=q45v5p939c0000001599280452541&qH=6a476f61ea33f248"))

# print(get_product_info_flipkart("https://www.flipkart.com/acer-nitro-5-ryzen-quad-core-8-gb-1-tb-hdd-windows-10-home-4-gb-graphics-amd-radeon-rx-560x-an515-42-r6gv-gaming-laptop/p/itmf6h2pyfu3y28x?pid=COMF6H2PJAYPCFZ6&lid=LSTCOMF6H2PJAYPCFZ6MQWULR&marketplace=FLIPKART&srno=s_1_1&otracker=AS_Query_HistoryAutoSuggest_1_4_na_na_na&otracker1=AS_Query_HistoryAutoSuggest_1_4_na_na_na&fm=SEARCH&iid=dc4832ae-24a1-467f-9c5c-b902b04ae212.COMF6H2PJAYPCFZ6.SEARCH&ppt=sp&ppn=sp&ssid=fn17h5n1vqafw0741599285826655&qH=6a476f61ea33f248"))

# print(get_product_info_flipkart("http://www.flipkart.com"))