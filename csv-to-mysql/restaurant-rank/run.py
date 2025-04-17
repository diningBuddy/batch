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
      'user': os.environ.get('MYSQL_USER', 'skku-user'),
      'password': os.environ.get('MYSQL_PASSWORD', 'skku-pw'),
      'database': os.environ.get('MYSQL_DB', 'skku')
    }

    logger.info("1. 카카오맵 순위 크롤링 시작 (카테고리별)")
    start_time = time.time()

    # 크롤링 실행
    try:
      subprocess.run(["python3", "kakao_rank.py"], check=True)
      logger.info(f"크롤링 완료: 카테고리별 CSV 파일 생성됨 (소요시간: {time.time() - start_time:.2f}초)")

      # 생성된 카테고리 파일 확인
      category_files = [f for f in os.listdir('.') if f.startswith('kakao_map_ranks_category_')]
      if category_files:
        logger.info(f"생성된 카테고리 파일: {', '.join(category_files)}")
      else:
        logger.warning("카테고리 파일이 생성되지 않았습니다.")

    except subprocess.CalledProcessError as e:
      logger.error(f"크롤링 실패: {str(e)}")

      # 기존 파일이 있는지 확인
      category_files = [f for f in os.listdir('.') if f.startswith('kakao_map_ranks_category_')]
      if not category_files:
        raise Exception("크롤링 실패 및 기존 카테고리 CSV 파일 없음")

      logger.warning(f"크롤링 실패했으나 기존 카테고리 CSV 파일 {len(category_files)}개를 사용해 계속 진행합니다.")

    logger.info("2. 카테고리별 데이터베이스 적재 시작")
    start_time = time.time()

    # 업데이트된 카테고리별 파일 처리를 위한 함수 임포트
    from update_restaurant_ranks import update_ranks

    # 현재 디렉토리 경로 전달
    result = update_ranks(db_config, '.')

    if result:
      logger.info(f"데이터베이스 적재 결과: 성공 {result.get('inserted', 0)}개, 매칭실패 {result.get('not_found', 0)}개, 오류 {result.get('error', 0)}개")

    logger.info(f"데이터베이스 적재 완료 (소요시간: {time.time() - start_time:.2f}초)")
    logger.info("전체 작업 완료!")

  except Exception as e:
    logger.error(f"오류 발생: {str(e)}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
  main()