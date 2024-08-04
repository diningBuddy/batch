MySql_batch  
=============
main.py 실행 시 MySql DB에 테이블을 생성하고 csv 데이터를 insert합니다.
기존에 존재하던 테이블(restaurants, restaurant_likes)을 모두 제거하고 다시 생성한 후 csv 파일의 데이터를 삽입합니다.

실행방법
-----------------
1. pymysql 라이브러리 설치
```
pip install pymysql
```
1-1. 또는 requirements.txt 실행
```
pip install -r requirements.txt
```
2. main.py 에서 localhost 주소를 필요시 변경해야 합니다.(Default: localhost:3306)
```
# connect to MySQL server
conn = pymysql.connect(
    host="127.0.0.1",  // 이 부분 필요 시 수정
    port=3306,
    user="skku-user",
    ...
    db="skku",
    charset='utf8'
)
```

TABLE 정보
-----------------
### restaurants

열 이름 | 설명 |타입 | Nullable | PK
---|---|---|---|---
`restaurant_id` | 식당 고유아이디 |BIGINT | NOT NULL | PK
`name` | 식당이름 | VARCHAR(64) NOT NULL | |
`category` | 식당 카테고리(ex. 돈가스, 보쌈) | VARCHAR(64) | |
`custom_category` | 음식점 종류(ex. 양식, 한식) | VARCHAR(64) | |
`review_count` | 리뷰 총 개수 | BIGINT | NOT NULL |
`like_count` | 좋아요 총 개수 |BIGINT | NOT NULL,
`address` | 주소 | VARCHAR(256) | |
`contact_num` | 전화번호 |VARCHAR(32) | |
`rating_avg` | 평점평균 | DOUBLE | |
`representative_image_url`| 대표 이미지 url 주소 | TEXT | |
`kingo_pass` | kingo pass 지원 여부 |TINYINT | |
`view_count` | 조회수 | BIGINT | |

### restaurant_likes

열 이름 | 설명 |타입 | Nullable | PK
---|---|---|---|---
`id` | 아이디(의미없음) | BIGINT | NOT NULL | PK
`restaurant_id` | 식당 고유아이디 | BIGINT | NOT NULL |
`user_id` | 유저 아이디 | BIGINT | NOT NULL |
`like` | 좋아요 여부 | TINYINT | NOT NULL |

CSV 파일 정보
--------------
### restaurants.csv
id|name|category|review_count|address|rating,number|image_url|custom_category
---|---|---|---|---|---|---|---
1|명동돈까스|돈가스|192|경기 수원시 장안구 서부로2106번길 17|4.7|031-297-7774||한식
2|목구멍 율전점|"육류,고기요리"|999+|경기 수원시 장안구 화산로233번길 46 1층,|031-293-9294||한식
...|
