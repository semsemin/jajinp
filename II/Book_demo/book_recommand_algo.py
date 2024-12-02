

from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from secrets_manager import get_api_key
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough

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

# 데이터 처리 함수
def process_book_data(all_responses):
    """
    책 데이터를 처리하여 추천 점수와 순위 기반 점수를 계산하는 함수.

    Args:
        all_responses (dict): 책 제목을 키로 하고, 리뷰 수, 별점, 베스트셀러 정보를 포함한 데이터를 값으로 가지는 딕셔너리.
            예: {
                "Book A": {"title": "Book A", "review_count": 1000, "rating": 4.5, "best_seller": 15},
                "Book B": {"title": "Book B", "review_count": 800, "rating": 4.8, "best_seller": 1},
                ...
            }

    Returns:
        pd.DataFrame: 추천 점수와 정규화된 순위 점수를 포함한 데이터프레임.
        list of dict: 각 책의 제목, 정규화된 별점, 추천 점수를 포함한 리스트.
    """
    processed_data = []

    for title, item in all_responses.items():
        try:
            # 필요한 값 처리
            rating = float(item.get("rating", 0))
            review_count = int(item.get("review_count", 0))
            best_seller = int(item.get("best_seller", 9999))  # 베스트셀러 순위가 없으면 기본값으로 큰 값 설정

            # 데이터 처리 결과 추가
            processed_data.append({
                "title": title,
                "rating": rating,
                "review_count": review_count,
                "best_seller_rank": best_seller
            })

        except (KeyError, ValueError) as e:
            print(f"Error processing book data for title '{title}': {e}")

    # 데이터를 데이터프레임으로 변환
    df = pd.DataFrame(processed_data)

    # 순위 기반 점수 계산
    df = assign_rank_based_score(df, "rating", ascending=False)  # 높은 별점이 우선
    df = assign_rank_based_score(df, "review_count", ascending=False)  # 리뷰 수가 많은 것이 우선
    df = assign_rank_based_score(df, "best_seller_rank", ascending=True)  # 베스트셀러 순위가 낮을수록(1위) 점수가 높음

    # 총 추천 점수 계산
    df['recommend_score'] = (
        df['rating_score'] +          # 별점 점수
        df['review_count_score'] +   # 리뷰 수 점수
        df['best_seller_rank_score'] # 베스트셀러 순위 점수
    )

    # 추천 점수 기준으로 정렬
    df = df.sort_values(by='recommend_score', ascending=False).reset_index(drop=True)

    # 추천 정보를 리스트로 변환
    recommendations = df[['title','recommend_score']].to_dict(orient='records')

    return df, recommendations