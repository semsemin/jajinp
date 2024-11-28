from langchain_core.documents import Document
from langchain_community.tools import TavilySearchResults
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from secrets_manager import get_api_key
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
import os
import json

def get_reviews_and_ratings(product_data):
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = get_api_key('GPT_API_KEY')
    os.environ["TAVILY_API_KEY"] = get_api_key('TAVILY_API_KEY')

    # Initialize GPT settings
    llm = ChatOpenAI(
        model='gpt-4o',
        temperature=0,
        max_tokens=500,
    )

    # Define prompt
    template = '''    
        You are a shopping assistant AI. Answer the question based on the context below.
        Respond in JSON format with keys 'review_count' and 'rating'.
        
        Context: {context}
        
        Question: {question}
        
        Response (JSON format):
    '''
    prompt = ChatPromptTemplate.from_template(template)

    # JSON Output Parser
    json_parser = JsonOutputParser()

    # Create chain
    chain = (
        {'context': RunnablePassthrough(), 'question': RunnablePassthrough()}
        | prompt
        | llm
        | json_parser
    )

    # Tavily search setup
    web_search = TavilySearchResults(max_results=10)

    # Store results
    all_responses = {}

    # Loop through products
    for product in product_data:
        query = f"{product['product_name']}에 대한 리뷰, 별점을 https://www.coupang.com 에서 검색해서 알려줘"

        # Perform Tavily search
        search_results = web_search.invoke(query)

        # Prepare context from search results
        context = "\n\n".join([f"URL: {result['url']}\n내용: {result['content']}" for result in search_results])

        # Run chain
        response = chain.invoke({'context': context, 'question': query})

        # Save results
        all_responses[product['product_name']] = {
            'product_name': product['product_name'],
            'review_count': response.get('review_count', 'N/A'),
            'rating': response.get('rating', 'N/A')
        }

    return all_responses