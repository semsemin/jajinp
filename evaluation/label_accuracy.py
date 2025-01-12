import base64
import json
import time
import pandas as pd
from openai import OpenAI
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from difflib import SequenceMatcher
from Levenshtein import distance  

client = OpenAI(api_key="{키번호}")

# 이미지 파일을 base64 인코딩
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 문자열 유사도 계산 함수
def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# OpenAI API를 통해 상품 데이터 가져오기
def get_product_data(image_path):
    base64_image = encode_image(image_path)
    start_time = time.time()

    # OpenAI API 요청
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in extracting product names and prices from price tags. Please locate each product label (up to 8 labels) within the image. For each label, extract the text *exactly as it appears on the label*, including any unique spellings, symbols, parentheses, or formatting. Extract the product name precisely as written, as though performing OCR, and capture any numbers as the price. Return the extracted information in JSON format without any line breaks or extra spaces. The format should be as follows: [{'product name': 'exact text from label for product name', 'price': 'price'}]. For multiple products, return a list of objects, omitting '$' or '원' symbols from the price so that only the numeric value remains."},
            {"role": "user", "content": [
                {"type": "text", "text": "Based on this data, please write the name and price in JSON format as [{\"product name\": \"exact text from label for product name\", \"price\": \"price\"}]. For multiple products, return a list of objects without '$' or '원' in price, just the number. Please read and transcribe each label's text exactly as it appears, capturing the unique spelling and formatting in the product name."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )

    response_content = response.choices[0].message.content
    print("API 응답 내용:", response_content)

    end_time = time.time()
    print(f"실행 시간: {end_time - start_time:.2f} 초")
    execution_time = end_time - start_time

    formatted_response = response_content.replace("'", '"')
    formatted_response = formatted_response.replace('\n', '').strip()
    cleaned_string = formatted_response.replace('json', '').strip()
    cleaned_string = cleaned_string.replace('```', '')  


    try:
        predicted_json = json.loads(cleaned_string)
    except json.JSONDecodeError:
        print("JSONDecodeError: 응답 내용을 JSON 형식으로 변환할 수 없습니다.")
        predicted_json = []

    return predicted_json, execution_time

# 성능 평가 함수 (전체 라벨에 대해 계산)
def evaluate_performance(actual_json, predicted_json, similarity_threshold=1.0):
    actual_labels = [(item["product name"], item["price"]) for item in actual_json]
    predicted_labels = [(item["product name"], item["price"]) for item in predicted_json]

    matched_count = 0
    for actual in actual_labels:
        for predicted in predicted_labels:
            name_similarity = string_similarity(actual[0], predicted[0])
            price_match = actual[1] == predicted[1]
            if name_similarity == similarity_threshold and price_match:
                matched_count += 1
                break

    total_actual = len(actual_labels)
    total_predicted = len(predicted_labels)
    
    accuracy = matched_count / total_actual if total_actual else 0
    precision = matched_count / total_predicted if total_predicted else 0
    recall = matched_count / total_actual if total_actual else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    return accuracy, precision, recall, f1

# 1-NED 계산 함수
def calculate_1_ned(actual_json, predicted_json):
    actual_labels = [(item["product name"], item["price"]) for item in actual_json]
    predicted_labels = [(item["product name"], item["price"]) for item in predicted_json]

    total_ned = []

    for actual, predicted in zip(actual_labels, predicted_labels):
        actual_text = actual[0] + str(actual[1])
        predicted_text = predicted[0] + str(predicted[1])

        # Edit Distance 계산
        edit_distance = distance(actual_text, predicted_text)
        max_len = max(len(actual_text), len(predicted_text))

        # 1-NED 계산
        if max_len > 0:
            ned = 1 - (edit_distance / max_len)
        else:
            ned = 1.0  # 빈 문자열인 경우 유사도를 1로 간주
        total_ned.append(ned)

    # 전체 평균 1-NED 계산
    overall_ned = sum(total_ned) / len(total_ned) if total_ned else 0

    print("Overall 1-NED:", overall_ned)
    return overall_ned

# WRA 계산 함수
def calculate_wra(actual_json, predicted_json):
    total_actual_words = 0
    total_matched_words = 0

    for actual_item, predicted_item in zip(actual_json, predicted_json):
        # 상품명과 가격을 단어로 나누기
        actual_words = actual_item["product name"].split() + [actual_item["price"]]
        predicted_words = predicted_item["product name"].split() + [predicted_item["price"]]

        # 실제 전체 단어 세기
        total_actual_words += len(actual_words)

        # 매치된 단어 세기
        matched_words = sum(1 for actual, predicted in zip(actual_words, predicted_words) if actual == predicted)
        total_matched_words += matched_words

    # WRA계산
    wra = total_matched_words / total_actual_words if total_actual_words > 0 else 0
    return wra


# 항목 수준 정확도 계산 함수
def calculate_item_accuracy(actual_json, predicted_json):
    matched_count = 0

    for actual_item in actual_json:
        actual_name = actual_item["product name"]
        actual_price = actual_item["price"]

        for predicted_item in predicted_json:
            predicted_name = predicted_item.get("product name", "")
            predicted_price = predicted_item.get("price", "")

            if actual_name == predicted_name and actual_price == predicted_price:
                matched_count += 1
                break

    return matched_count / len(actual_json)


# 엑셀 데이터 처리 및 테스트 수행
def process_excel_and_evaluate(excel_path,output_path):
    df = pd.read_excel(excel_path)
    df.dropna(subset=['파일 경로(번호)'], inplace=True)  # 파일 경로가 없는 행은 제거

    print("엑셀 열 이름:", df.columns.tolist())  # 열 이름 확인

    results = []

    for index, row in df.iterrows():
        image_path = f"{파일경로}/{row['파일 경로(번호)']}.jpg"
        try:
            # JSON 문자열을 파싱하여 리스트로 변환
            actual_json = json.loads(f"[{row['actual data']}]")
        except (TypeError, json.JSONDecodeError):
            print(f"[테스트 {index + 1}] JSONDecodeError: {row['actual data']}은(는) 유효하지 않은 JSON입니다.")
            continue

        # 예측 데이터 가져오기
        predicted_json, execution_time = get_product_data(image_path)
        print(f"\n[테스트 {index + 1}] 파일 경로: {image_path}")
        print("실제 데이터:", actual_json)
        print("예측 데이터:", predicted_json)
        accuracy, precision, recall, f1 = evaluate_performance(actual_json, predicted_json)
        item_accuracy = calculate_item_accuracy(actual_json, predicted_json)
        wra = calculate_wra(actual_json, predicted_json)
        overall_ned = calculate_1_ned(actual_json, predicted_json)   
        # 결과 저장
        results.append({
            "테스트 번호": index + 1,
            "파일 경로": image_path,
            "실제 데이터": actual_json,
            "예측 데이터": predicted_json,
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1 Score": f1,
            "WRA": wra,
            "1-NED": overall_ned,
            "항목 수준 정확도": item_accuracy,
            "실행 시간 (초)": execution_time,
        })

    # 결과를 DataFrame으로 변환 후 엑셀 저장
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"결과가 저장되었습니다: {output_path}")

# 엑셀 파일 경로
data_excel_path = "{정답데이터셋 경로}"
output_excel_path = "{결과 저장할 경로}"
process_excel_and_evaluate(data_excel_path,output_excel_path)