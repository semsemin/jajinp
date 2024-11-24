import streamlit as st
from product_data import fetch_online_product_data
from naver_review import fetch_and_display_review_summary

def display_sorted_products():
    "Streamlit 탭에서 리뷰 수, 최저가, 평점을 기준으로 정렬된 상품 데이터를 표시하는 함수"
    # Load product data from session state
    product_data = st.session_state["product_data"]

    # 데이터 정제: NoneType 값을 기본값으로 대체
    for product in product_data:
        product["review_count"] = int(product["review_count"]) if product["review_count"] and product["review_count"] != "N/A" else 0
        product["online_price"] = int(product["online_price"]) if product["online_price"] and product["online_price"] != "N/A" else float('inf')
        product["rating"] = float(product["rating"]) if product["rating"] and product["rating"] != "N/A" else 0.0

    # Sort data once and store in session state
    if "sorted_by_reviews" not in st.session_state:
        st.session_state["sorted_by_reviews"] = sorted(
            product_data, key=lambda x: x["review_count"], reverse=True
        )
    if "sorted_by_price" not in st.session_state:
        st.session_state["sorted_by_price"] = sorted(
            product_data, key=lambda x: x["online_price"]
        )
    if "sorted_by_rating" not in st.session_state:
        st.session_state["sorted_by_rating"] = sorted(
            product_data, key=lambda x: x["rating"], reverse=True
        )

    # Create Streamlit tabs
    tab1, tab2, tab3 = st.tabs(["리뷰순", "최저가순", "평점순"])

    # Define how each tab should display
    for tab, sorted_products, title, highlight_field, highlight_label in zip(
        [tab1, tab2, tab3],
        [st.session_state["sorted_by_reviews"], st.session_state["sorted_by_price"], st.session_state["sorted_by_rating"]],
        ["리뷰 순위", "최저가 순위", "평점 순위"],
        ["review_count", "online_price", "rating"],
        ["리뷰 수", "최저가", "평점"]
    ):
        with tab:
            st.subheader(title)
            for idx, product in enumerate(sorted_products, start=1):
                # Display product details
                st.markdown(f"### {idx}. {product['product_name']}")

                # Highlight the sorted field with larger, bold text
                highlighted_value = ""
                if highlight_field == "review_count":
                    highlighted_value = f"{product['review_count']}회"
                elif highlight_field == "online_price":
                    highlighted_value = f"{product['online_price']}원"
                elif highlight_field == "rating":
                    highlighted_value = f"{product['rating']}점"

                st.markdown(f"<h4 style='font-weight:bold; font-size:1.2em;'>- {highlight_label}: {highlighted_value}</h4>", unsafe_allow_html=True)

                # Display other details
                other_details = {
                    "review_count": f"- 리뷰 수: {product['review_count']}회",
                    "online_price": f"- 최저가: {product['online_price']}원",
                    "rating": f"- 평점: {product['rating']}점"
                }
                # Exclude the highlighted field
                for key, value in other_details.items():
                    if key != highlight_field:
                        st.markdown(value)

                # Fetch and display one-line review summary
                with st.spinner("한줄평을 가져오는 중..."):
                    summary = fetch_and_display_review_summary(product["product_name"])
                    if summary:
                        st.markdown(f"**한줄평:** {summary}")
                    else:
                        st.warning("한줄평을 가져올 수 없습니다.")
                st.markdown("---")
