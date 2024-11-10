import base64
import time
from openai import OpenAI
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from secrets_manager import get_secret_key


gpt_key = get_secret_key()
client = OpenAI(api_key=gpt_key)

# 이미지 파일을 base64 인코딩
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# API 호출 및 응답 처리
def get_product_data(image_path):
    base64_image = encode_image(image_path)
    start_time = time.time()  # 시작 시간

    # OpenAI API 요청
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting product names and prices from price tags. Please locate each product label (up to 8 labels) within the image. For each label, extract the text *exactly as it appears on the label*, including any unique spellings, symbols, parentheses, or formatting. Extract the product name precisely as written, as though performing OCR, and capture any numbers as the price. Return the extracted information in JSON format without any line breaks or extra spaces. The format should be as follows: [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects, omitting '원' or '₩' symbols from the price so that only the numeric value remains."},
            {"role": "user", "content": [
                {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects without '원' or '₩' in price, just the number. Please read and transcribe each label's text exactly as it appears, capturing the unique spelling and formatting in the product name."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )

    # 응답 내용을 확인하기 위해 출력
    response_content = response.choices[0].message.content
    print("API 응답 내용:", response_content)  # 응답 내용 출력

    end_time = time.time()  # 실행 시간 측정 종료
    execution_time = end_time - start_time
    print(f"실행 시간: {execution_time:.2f} 초")
    print(response_content)

    formatted_response = response_content.replace("'", '"')
    formatted_response = formatted_response.replace('\n', '').strip()
    cleaned_string = formatted_response.replace('json', '').strip()
    cleaned_string = cleaned_string.replace('```', '')  

    print(cleaned_string)
    try:
        predicted_json = json.loads(cleaned_string)
    except json.JSONDecodeError:
        print("JSONDecodeError: 응답 내용을 JSON 형식으로 변환할 수 없습니다.")
        predicted_json = []
    
    return predicted_json

# 실제 값과 예측 값 비교 및 성능 평가
def evaluate_performance(actual_json, predicted_json):
    # JSON 데이터에서 상품명과 가격을 튜플 형식으로 변환
    actual_labels = [(item["product name"], item["price"]) for item in actual_json]
    predicted_labels = [(item["product name"], item["price"]) for item in predicted_json]

    # 예측 값이 비어 있는 경우 처리
    if not predicted_labels:
        print("예측 값이 없습니다. 성능 평가를 생략합니다.")
        return
    
        # 실제 값 개수가 예측 값 개수보다 많을 경우, 누락된 예측 값 채우기
    if len(predicted_labels) < len(actual_labels):
        missing_count = len(actual_labels) - len(predicted_labels)
        # 잘못된 값으로 채우기
        predicted_labels.extend([("라벨 수 인식 오류", "0")] * missing_count)
    
    # 정확도, 정밀도, 재현율, F1 스코어 계산
    accuracy = accuracy_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels])
    precision = precision_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')
    recall = recall_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')
    f1 = f1_score([label[0] for label in actual_labels], [label[0] for label in predicted_labels], average='macro')

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    

# 이미지 경로와 실제 값 정의
image_path = "/Users/songjuhui/Desktop/testset/8-4.JPG"
actual_json = [{"product name": "아이디얼포맨 퍼펙트올인원 상시기획", "price": "20900"},{"product name": "아이디얼포맨 시카올인원 상시기획", "price": "19900"},{"product name": "아이디얼포맨 프레시올인원 상시기획", "price": "19900"},{"product name": "아이디얼포맨 선올인원 상시 기획", "price": "20900"},{"product name": "아이디얼포맨 퍼펙트 탄력스킨", "price": "15900"},{"product name": "아이디얼포맨 퍼펙트탄력로션 150mL", "price": "16900"},{"product name": "아이디얼포맨 퍼펙트탄력스킨케어2종세트", "price": "32800"},{"product name": "아이디얼포맨 퍼펙트클렌징 올인원폼", "price": "8900"},
]
# 예측 데이터 가져오기
predicted_json = get_product_data(image_path)

print(actual_json)

# 성능 평가
evaluate_performance(actual_json, predicted_json) 