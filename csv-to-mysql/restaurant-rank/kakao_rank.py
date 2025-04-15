from playwright.sync_api import sync_playwright
import json
import pandas as pd
import logging
import sys
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def crawl_kakao_map_ranks(categories=None):
  try:
    logger.info("카카오맵 데이터 크롤링 시작...")

    try:
      restaurants_df = pd.read_csv("kakao_restaurants.csv")
      restaurant_names_dict = {name: True for name in restaurants_df['name']}
      logger.info(f"{len(restaurant_names_dict)}개 레스토랑 로드 완료")
    except Exception as e:
      logger.error(f"kakao_restaurants.csv 로드 실패: {str(e)}", exc_info=True)
      raise

    all_parsed_data = []

    with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)

      for category in categories:
        logger.info(f"카테고리 '{category}' 크롤링 시작")
        page = browser.new_page()
        url = f"https://app.map.kakao.com/rank/places/search.json?appVersion=5.18.1&category-or-menu={category}&deviceModel=iPhone%2014%20Pro&lang=ko&limit=100&osVersion=17.5.1&pf=iOS&region=B22880600&serviceName=kakaomap&type=search"

        try:
          page.goto(url)
          time.sleep(2)

          pre = page.query_selector("pre")
          if not pre:
            logger.warning(f"카테고리 '{category}'에서 데이터를 찾을 수 없음")
            page.close()
            continue

          data = json.loads(pre.inner_text())
          items = data.get("items", [])

          category_parsed_data = []
          index = 1

          for item in items:
            restaurant_name = item.get("name")

            if restaurant_name in restaurant_names_dict:
              address = ""
              if "regions" in item and item["regions"]:
                sorted_regions = sorted(item["regions"], key=lambda x: x.get("depth", 0))
                address = " ".join([region.get("name", "") for region in sorted_regions])

              category_parsed_data.append({
                "rank": index,
                "name": restaurant_name,
                "lat": item.get("lat"),
                "lon": item.get("lon"),
                "category": category,
                "category_name": item.get("category_name"),
                "review_count": item.get("review_count"),
                "review_rating": item.get("review_rating"),
                "thumbnail": item.get("thumbnail"),
                "address": address,
              })
              index += 1

          if category_parsed_data:
            category_df = pd.DataFrame(category_parsed_data)
            filename = f"kakao_map_ranks_{category}.csv"
            category_df.to_csv(filename, index=False, encoding="utf-8-sig")
            logger.info(f"CSV 파일 저장 완료: {filename} ({len(category_parsed_data)}개 항목)")

          all_parsed_data.extend(category_parsed_data)

        except Exception as e:
          logger.error(f"카테고리 '{category}' 크롤링 중 오류: {str(e)}")

        finally:
          page.close()

      browser.close()

    if all_parsed_data:
      df = pd.DataFrame(all_parsed_data)
      combined_filename = "kakao_map_ranks_all_categories.csv"
      df.to_csv(combined_filename, index=False, encoding="utf-8-sig")
      logger.info(f"통합 CSV 파일 저장 완료: {combined_filename} (총 {len(all_parsed_data)}개 항목)")

    return "크롤링 완료"

  except Exception as e:
    logger.error(f"크롤링 중 오류 발생: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
  categories = [
    "category_all",
    "category_korean",
    "category_japanese",
    "category_western"
  ]
  crawl_kakao_map_ranks(categories)