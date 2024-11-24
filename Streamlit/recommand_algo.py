import openai
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from secrets_manager import get_api_key
from langchain_openai import OpenAIEmbeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# OpenAI API Key 설정
os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')

# 최대 별점 추정 함수
def estimate_max_rating(rating):
    if rating > 5:  # 별점이 5점을 초과하면 10점 만점으로 간주
        return 10
    return 5

def generate_content_based_recommendations(local_data, online_data):
    # 현장과 온라인 정보 결합
    merged_data = []
    for local_item in local_data:
        for online_item in online_data:
            if local_item["product_name"] == online_item["product_name"]:
                max_rating = estimate_max_rating(online_item["rating"])  # 최대 별점 추정
                normalized_rating = (online_item["rating"] / max_rating) * 5  # 별점 정규화
                merged_data.append({
                    "product_name": local_item["product_name"],
                    "local_price": local_item["price"],
                    "online_price": online_item["online_price"],
                    "review_count": online_item["review_count"],
                    "rating": online_item["rating"],
                    "normalized_rating": normalized_rating,  # 정규화된 별점 추가
                    "recommend_score": 0  # Placeholder for recommendation score
                })

    df = pd.DataFrame(merged_data)

    # 문자열로 저장된 가격을 숫자로 변환
    df['local_price'] = pd.to_numeric(df['local_price'], errors='coerce').fillna(0).astype(float)
    df['online_price'] = pd.to_numeric(df['online_price'], errors='coerce').fillna(0).astype(float)

    # Step 2: 추천 점수 계산
    df['price_difference'] = abs(df['local_price'] - df['online_price'])
    df['recommend_score'] = (
        df['review_count'] * 0.2 +
        df['rating'] * 100 * 0.6 -
        df['price_difference'] * 0.2
    )
    df = df.sort_values(by='recommend_score', ascending=False)

    # Step 3: 유사도 계산
    product_names = df['product_name'].tolist()
    embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    embeddings = [embeddings_model.embed_query(name) for name in product_names]

    # TF-IDF 유사도 계산
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(product_names)
    tfidf_similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 임베딩 유사도 계산
    similarity_matrix = cosine_similarity(embeddings, embeddings)

    # TF-IDF와 임베딩 유사도 결합
    combined_similarity_matrix = (0.5 * tfidf_similarity_matrix) + (0.5 * similarity_matrix)

    # Step 4: 유사 상품 추천 생성
    recommendations = []
    for idx, product in enumerate(product_names):
        similar_indices = combined_similarity_matrix[idx].argsort()[::-1][1:]  # Exclude self
        similar_items = [(product_names[i], combined_similarity_matrix[idx][i]) 
                         for i in similar_indices if combined_similarity_matrix[idx][i] > 0.1]
        recommendations.append({
            "product_name": product,
            "recommendations": similar_items
        })

    return df, recommendations

