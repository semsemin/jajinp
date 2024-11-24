import json
from naver_lowest import get_naver_api_credentials, search_product, parse_json_response
from Tavily_chroma import get_reviews_and_ratings


def fetch_online_product_data(product_data):
    client_id, client_secret = get_naver_api_credentials()
    result_data = []

    for product in product_data:
        product_name = product["product_name"]

        # Fetch lowest price details
        json_response = search_product(product_name, client_id, client_secret)
        if json_response:
            lowest_price_data = parse_json_response(json_response)
            if lowest_price_data:
                lowest_price = lowest_price_data.get("lowest_price", "N/A")
            else:
                lowest_price = "N/A"
        else:
            lowest_price = "N/A"

        # Fetch review and rating details
        review_rating_data = get_reviews_and_ratings([{"product_name": product_name}])
        review_count = review_rating_data.get(product_name, {}).get("review_count", "N/A")
        rating = review_rating_data.get(product_name, {}).get("rating", "N/A")

        # Combine data
        result_data.append({
            "product_name": product_name,
            "review_count": review_count,
            "rating": rating,
            "online_price": lowest_price
        })

    return result_data
