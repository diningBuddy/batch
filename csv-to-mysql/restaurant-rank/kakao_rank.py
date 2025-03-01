import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def crawl_kakao_map_ranks():
  try:
    # Load kakao_restaurants.csv
    logger.info("레스토랑 목록 로드 중...")
    restaurants_df = pd.read_csv("kakao_restaurants.csv")
    restaurant_names_dict = {name: True for name in restaurants_df['name']}
    logger.info(f"{len(restaurant_names_dict)}개 레스토랑 로드 완료")

    # Configure Selenium WebDriver for Docker environment
    logger.info("웹드라이버 설정 중...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Docker 환경에서 실행될 경우 chromedriver 경로 직접 지정
    try:
      driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except:
      logger.info("ChromeDriverManager 실패, 경로 직접 지정 시도")
      driver = webdriver.Chrome(options=options)

    # Access the URL
    logger.info("카카오맵 API 접근 중...")
    url = "https://app.map.kakao.com/rank/places/search.json?appVersion=5.18.1&category-or-menu=category_all&deviceModel=iPhone%2014%20Pro&lang=ko&limit=100&osVersion=17.5.1&pf=iOS&region=B22880600&serviceName=kakaomap&type=search"
    driver.get(url)

    # Retrieve the JSON data
    pre = driver.find_element(By.TAG_NAME, "pre").text
    data = json.loads(pre)

    # Close the WebDriver
    driver.quit()
    logger.info("데이터 가져오기 완료")

    # Parse JSON data
    items = data['items']
    parsed_data = []
    index = 1

    logger.info("데이터 파싱 중...")
    for item in items:
      restaurant_name = item.get("name")

      if restaurant_name in restaurant_names_dict:
        # 지역 정보에서 주소 구성
        address = ""
        if "regions" in item and item["regions"]:
          sorted_regions = sorted(item["regions"], key=lambda x: x.get("depth", 0))
          address = " ".join([region.get("name", "") for region in sorted_regions])

        parsed_data.append({
          "rank": index,
          "name": restaurant_name,
          "lat": item.get("lat"),
          "lon": item.get("lon"),
          "category_name": item.get("category_name"),
          "review_count": item.get("review_count"),
          "review_rating": item.get("review_rating"),
          "thumbnail": item.get("thumbnail"),
          "address": address,
        })
        index += 1

    # Check if we found any matching restaurants
    if not parsed_data:
      logger.warning("매칭되는 레스토랑이 없습니다!")
    else:
      logger.info(f"{len(parsed_data)}개 레스토랑 매칭됨")

    # Create DataFrame and save to CSV
    df = pd.DataFrame(parsed_data)
    df.to_csv("kakao_map_ranks.csv", index=False, encoding="utf-8-sig")
    logger.info("CSV 파일 생성 완료: kakao_map_ranks.csv")

    return "kakao_map_ranks.csv"

  except Exception as e:
    logger.error(f"크롤링 중 오류 발생: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
  crawl_kakao_map_ranks()