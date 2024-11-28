import base64
import time
from openai import OpenAI
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from II.secrets_manager import get_api_key


gpt_key = get_api_key(api_name='GPT_API_KEY')
client = OpenAI(api_key=gpt_key)

# ?��미�?? ?��?��?�� base64 ?��코딩
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# API ?���? �? ?��?�� 처리
def get_product_data(image_path):
    base64_image = encode_image(image_path)
    start_time = time.time()  # ?��?�� ?���?

    # OpenAI API ?���?
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting product names and prices from price tags. Please locate each product label (up to 8 labels) within the image. For each label, extract the text *exactly as it appears on the label*, including any unique spellings, symbols, parentheses, or formatting. Extract the product name precisely as written, as though performing OCR, and capture any numbers as the price. Return the extracted information in JSON format without any line breaks or extra spaces. The format should be as follows: [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects, omitting '?��' or '?��' symbols from the price so that only the numeric value remains."},
            {"role": "user", "content": [
                {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects without '?��' or '?��' in price, just the number. Please read and transcribe each label's text exactly as it appears, capturing the unique spelling and formatting in the product name."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )

    # ?��?�� ?��?��?�� ?��?��?���? ?��?�� 출력
    response_content = response.choices[0].message.content
    print("API ?��?�� ?��?��:", response_content)  # ?��?�� ?��?�� 출력

    end_time = time.time()  # ?��?�� ?���? 측정 종료
    execution_time = end_time - start_time
    print(f"?��?�� ?���?: {execution_time:.2f} �?")
    print(response_content)

    formatted_response = response_content.replace("'", '"')
    formatted_response = formatted_response.replace('\n', '').strip()
    cleaned_string = formatted_response.replace('json', '').strip()
    cleaned_string = cleaned_string.replace('```', '')  

    print(cleaned_string)
    try:
        predicted_json = json.loads(cleaned_string)
    except json.JSONDecodeError:
        print("JSONDecodeError: ?��?�� ?��?��?�� JSON ?��?��?���? �??��?�� ?�� ?��?��?��?��.")
        predicted_json = []
    
    return predicted_json

# ?��?�� 값과 ?���? �? 비교 �? ?��?�� ?���?
def evaluate_performance(actual_json, predicted_json):
    # JSON ?��?��?��?��?�� ?��?��명과 �?격을 ?��?�� ?��?��?���? �??��
    actual_labels = [(item["product name"], item["price"]) for item in actual_json]
    predicted_labels = [(item["product name"], item["price"]) for item in predicted_json]

    # ?���? 값이 비어 ?��?�� 경우 처리
    if not predicted_labels:
        print("?���? 값이 ?��?��?��?��. ?��?�� ?���?�? ?��?��?��?��?��.")
        return
    
        # ?��?�� �? 개수�? ?���? �? 개수보다 많을 경우, ?��?��?�� ?���? �? 채우�?
    if len(predicted_labels) < len(actual_labels):
        missing_count = len(actual_labels) - len(predicted_labels)
        # ?��못된 값으�? 채우�?
        predicted_labels.extend([("?���? ?�� ?��?�� ?���?", "0")] * missing_count)
    
    # ?��?��?��, ?���??��, ?��?��?��, F1 ?��코어 계산
    accuracy = accuracy_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels])
    precision = precision_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')
    recall = recall_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')
    f1 = f1_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    

# ?��미�?? 경로??? ?��?�� �? ?��?��
image_path = "/Users/songjuhui/Desktop/testset/8-4.JPG"
actual_json = [{"product name": "?��?��?��?��?���? ?��?��?��?��?��?�� ?��?��기획", "price": "20900"},{"product name": "?��?��?��?��?���? ?��카올?��?�� ?��?��기획", "price": "19900"},{"product name": "?��?��?��?��?���? ?��?��?��?��?��?�� ?��?��기획", "price": "19900"},{"product name": "?��?��?��?��?���? ?��?��?��?�� ?��?�� 기획", "price": "20900"},{"product name": "?��?��?��?��?���? ?��?��?�� ?��?��?��?��", "price": "15900"},{"product name": "?��?��?��?��?���? ?��?��?��?��?��로션 150mL", "price": "16900"},{"product name": "?��?��?��?��?���? ?��?��?��?��?��?��?���??��2종세?��", "price": "32800"},{"product name": "?��?��?��?��?���? ?��?��?��?��?���? ?��?��?��?��", "price": "8900"},
]
# ?���? ?��?��?�� �??��?���?
predicted_json = get_product_data(image_path)

print(actual_json)

# ?��?�� ?���?
evaluate_performance(actual_json, predicted_json) 