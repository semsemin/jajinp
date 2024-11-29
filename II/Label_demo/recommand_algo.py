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

# 순위 기반 점수 부여 함수
def assign_rank_based_score(df, column_name, ascending=True):
    """
    해당 컬럼(column_name)을 기준으로 동일한 값에 대해 같은 점수를 부여.
    ascending=True일 경우 오름차순(작은 값이 높은 순위).
    """
    df = df.sort_values(by=column_name, ascending=ascending).reset_index(drop=True)
    max_score = 100
    step = 10
    scores = []
    rank = 0
    prev_value = None

    for idx, value in enumerate(df[column_name]):
        if value != prev_value:  # 값이 변하면 순위 갱신
            rank = idx
        score = max(max_score - rank * step, 0)
        scores.append(score)
        prev_value = value

    df[f"{column_name}_score"] = scores
    return df

# 추천 생성 함수
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
                    "normalized_rating": normalized_rating  # 정규화된 별점 추가
                })

    df = pd.DataFrame(merged_data)

    # 문자열로 저장된 가격을 숫자로 변환
    df['local_price'] = pd.to_numeric(df['local_price'], errors='coerce').fillna(0).astype(float)
    df['online_price'] = pd.to_numeric(df['online_price'], errors='coerce').fillna(0).astype(float)

    # 가격 차이 계산
    df['price_difference'] = abs(df['local_price'] - df['online_price'])

    # 별점, 리뷰 수, 가격 차이에 대해 각각 순위 점수 부여
    df = assign_rank_based_score(df, "rating", ascending=False)  # 높은 별점이 우선
    df = assign_rank_based_score(df, "review_count", ascending=False)  # 리뷰 수가 많은 것이 우선
    df = assign_rank_based_score(df, "price_difference", ascending=True)  # 가격 차이가 작은 것이 우선

    # 총 추천 점수 계산
    df['recommend_score'] = (
        df['rating_score'] +          # 별점 점수
        df['review_count_score'] +   # 리뷰 수 점수
        df['price_difference_score'] # 가격 차이 점수
    )

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
