from playwright.sync_api import sync_playwright
import json
import pandas as pd
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def crawl_kakao_map_ranks():
  try:
    logger.info("카카오맵 데이터 크롤링 시작...")

    try:
      restaurants_df = pd.read_csv("kakao_restaurants.csv")
      restaurant_names_dict = {name: True for name in restaurants_df['name']}
      logger.info(f"{len(restaurant_names_dict)}개 레스토랑 로드 완료")
    except Exception as e:
      logger.error(f"kakao_restaurants.csv 로드 실패: {str(e)}", exc_info=True)
      raise

    with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      page = browser.new_page()
      url = "https://app.map.kakao.com/rank/places/search.json?appVersion=5.18.1&category-or-menu=category_all&deviceModel=iPhone%2014%20Pro&lang=ko&limit=100&osVersion=17.5.1&pf=iOS&region=B22880600&serviceName=kakaomap&type=search"
      page.goto(url)

      pre = page.query_selector("pre")
      if not pre:
        raise Exception("데이터를 찾을 수 없음")

      data = json.loads(pre.inner_text())
      browser.close()

    items = data.get("items", [])
    parsed_data = []
    unmatched_restaurants = []
    index = 1

    for item in items:
      restaurant_name = item.get("name")

      if restaurant_name in restaurant_names_dict:
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
      else:
        unmatched_restaurants.append(restaurant_name)

    df = pd.DataFrame(parsed_data)
    df.to_csv("kakao_map_ranks.csv", index=False, encoding="utf-8-sig")
    logger.info("CSV 파일 저장 완료: kakao_map_ranks.csv")

    return "kakao_map_ranks.csv"

  except Exception as e:
    logger.error(f"크롤링 중 오류 발생: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
  crawl_kakao_map_ranks()
