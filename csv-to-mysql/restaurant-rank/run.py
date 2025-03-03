import os
import logging
import sys
import subprocess
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
  try:
    db_config = {
      'host': os.environ.get('MYSQL_HOST', 'mysql'),
      'port': int(os.environ.get('MYSQL_PORT', 3306)),
      'user': os.environ.get('MYSQL_USER', 'root'),
      'password': os.environ.get('MYSQL_PASSWORD', '1234'),
      'database': os.environ.get('MYSQL_DB', 'skku')
    }

    logger.info("1. 카카오맵 순위 크롤링 시작")
    start_time = time.time()

    try:
      subprocess.run(["python3", "kakao_rank.py"], check=True)
      logger.info(f"크롤링 완료: kakao_map_ranks.csv (소요시간: {time.time() - start_time:.2f}초)")
    except subprocess.CalledProcessError as e:
      logger.error(f"크롤링 실패: {str(e)}")
      if not os.path.exists("kakao_map_ranks.csv"):
        raise Exception("크롤링 실패 및 기존 CSV 파일 없음")
      logger.warning("크롤링 실패했으나 기존 CSV 파일을 사용해 계속 진행합니다.")

    logger.info("2. 데이터베이스 적재 시작")
    start_time = time.time()

    from update_restaurant_ranks import insert_ranks
    insert_ranks(db_config, "kakao_map_ranks.csv")

    logger.info(f"데이터베이스 적재 완료 (소요시간: {time.time() - start_time:.2f}초)")
    logger.info("전체 작업 완료!")

  except Exception as e:
    logger.error(f"오류 발생: {str(e)}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
  main()