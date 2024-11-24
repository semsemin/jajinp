import urllib.request
import json
from Streamlit.secrets_manager import get_api_key

def get_naver_api_credentials():
    client_id = get_api_key(api_name='CLIENT_ID')
    client_secret = get_api_key(api_name='CLIENT_SECRET')
    return client_id, client_secret

def search_product(product_name, client_id, client_secret):
    query = urllib.parse.quote(product_name)
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=5"

    request = urllib.request.Request(url)
    request.add_header('X-Naver-Client-Id', client_id)
    request.add_header('X-Naver-Client-Secret', client_secret)

    try:
        response = urllib.request.urlopen(request)
        response_code = response.getcode()
        response_body = response.read().decode('utf-8')

        if response_code != 200:
            print(f"Error: Received response code {response_code}")
            print(response_body)
            return None

        return response_body
    except Exception as e:
        print(f"Error: Failed to connect to the Naver API. {str(e)}")
        return None

def parse_json_response(json_data):
    try:
        data = json.loads(json_data)
        items = data.get("items", [])

        product_info = []
        lowest_price = float('inf')
        lowest_price_link = ""
        title = ""

        for item in items:
            price = int(item["lprice"])
            title = item["title"]
            product_info.append({
                "title": title,
                "link": item["link"],
                "price": price,
                "mallName": item["mallName"]
            })

            if price < lowest_price:
                lowest_price = price
                lowest_price_link = item["link"]

        return {
            "lowest_price": lowest_price,
            "lowest_price_link": lowest_price_link,
            "title": title,
            "products": product_info
        }
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON. The response may not be in JSON format.")
        print("Response content:", json_data)
        return None

def get_lowest_prices(product_data):
    client_id, client_secret = get_naver_api_credentials()
    result_data = {}

    for product in product_data:
        product_name = product["product_name"]  # Updated to match the key in sorting.py
        json_response = search_product(product_name, client_id, client_secret)

        if json_response:
            parsed_result = parse_json_response(json_response)
            if parsed_result:
                result_data[product_name] = parsed_result

    return result_data
