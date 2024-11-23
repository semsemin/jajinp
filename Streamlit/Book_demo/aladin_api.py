import os
import sys
import requests
import json
from secrets_manager import get_api_key

# API 키와 URL 설정
TTBKey = get_api_key('ALADIN_API_KEY')
query = '알라딘'
url = f"http://www.aladin.co.kr/ttb/api/ItemSearch.aspx?ttbkey={TTBKey}&Query={query}&QueryType=Title&MaxResults=5&SearchTarget=Book&output=js&Version=20131101"

# API 요청
response = requests.get(url)
print(response.text)

# # 응답 처리
# if response.status_code == 200:
#     data = response.json()
#     for item in data['item']:
#         title = item['title']
#         description = item.get('description', '줄거리 없음')
#         print(f"제목: {title}\n줄거리: {description}\n")
# else:
#     print(f"API 요청 실패: {response.status_code}")