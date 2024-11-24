import openai
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from secrets_manager import get_api_key
from langchain_openai import OpenAIEmbeddings
import os

# OpenAI API Key 설정
os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')

# 예시 데이터
local_data = [
    {"product_name": "동원 매운고추참치90g", "price": 3300},
    {"product_name": "동원 야채참치90g", "price": 3300},
    {"product_name": "동원 고추참치100g", "price": 2800}
]

online_data = [
    {"product_name": "동원 매운고추참치90g", "review_count": 302, "rating": 5, "online_price": 2900},
    {"product_name": "동원 야채참치90g", "review_count": 9020, "rating": 4.7, "online_price": 3100},
    {"product_name": "동원 고추참치100g", "review_count": 1020, "rating": 4.5, "online_price": 3000}
]

# 최대 별점 추정 함수
def estimate_max_rating(rating):
    if rating > 5:  # 별점이 5점을 초과하면 10점 만점으로 간주
        return 10
    return 5

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

# 데이터를 데이터 프레임으로 변환
df = pd.DataFrame(merged_data)

# 점수 계산 (정규화된 별점 기반)
df['price_difference'] = abs(df['local_price'] - df['online_price'])
df['recommend_score'] = (
    df['review_count'] * 0.2 +  # 리뷰 수 가중치
    df['normalized_rating'] * 0.3 +  
    df['price_difference'] * 0.5  # 가격 차이 페널티
)

# 추천 점수에 따라 sort
df = df.sort_values(by='recommend_score', ascending=False)

# 상품명 데이터 
product_names = [item["product_name"] for item in local_data]

# LangChain OpenAI Embeddings 생성
embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
embeddings = [embeddings_model.embed_query(name) for name in product_names]


# TF-IDF 유사도 계산
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(product_names)
tfidf_similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 유사도 계산
similarity_matrix = cosine_similarity(embeddings, embeddings)

# TF-IDF와 임베딩 유사도 결합
combined_similarity_matrix = (0.5 * tfidf_similarity_matrix) + (0.5 * similarity_matrix)

# 컨텐츠 기반 추천(재고가 없을 시 가장 비슷한 유사품 추천)
recommendations = []
for idx, product in enumerate(product_names):
    similar_indices = similarity_matrix[idx].argsort()[::-1][1:]  # Exclude self
    similar_items = [(product_names[i], similarity_matrix[idx][i]) for i in similar_indices if similarity_matrix[idx][i] > 0.1]
    recommendations.append({
        "product_name": product,
        "recommendations": similar_items
    })

# 출력
print("\nSorted Products by Recommendation Score:")
print(df[['product_name', 'recommend_score', 'local_price', 'online_price', 'review_count', 'rating']])

print("\nContent-based Recommendations:")
for rec in recommendations:
    print(rec)



