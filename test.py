import logging
from flask import Flask
from dbcl import DBconnector

app = Flask(__name__, static_url_path='/static')

# DB 연결 객체 생성
childdb = DBconnector('CHILD')
calledb = DBconnector('CALL_E')
counselordb = DBconnector('COUNSELOR')
child_infodb = DBconnector('CHILD_INFO')
review_listdb = DBconnector('REVIEW')

# 아동 상담 분야 가져오기
def get_all_child_survey_consulting():
    query = "SELECT child_id, survey_consulting FROM CHILD_INFO.child_info_list"
    result = child_infodb.execute(query)
    return result

# 상담사 상담 분야 가져오기
def get_all_counselor_survey_consulting():
    query = "SELECT co_id, co_consulting FROM COUNSELOR.counselor_list"
    result = counselordb.execute(query)
    return result

# child_id 별로 모든 상담사와의 일치 여부를 확인하여 점수 부여
def calculate_scores_for_all():
    child_survey_consulting = get_all_child_survey_consulting()
    counselor_survey_consulting = get_all_counselor_survey_consulting()

    scores = {}

    for child_row in child_survey_consulting:
        child_id, child_consulting = child_row

        scores[child_id] = {}

        for co_id, co_consulting in counselor_survey_consulting:
            score = 40 if all(survey_consulting in co_consulting.split(', ') for survey_consulting in
                              child_consulting.split(', ')) else 0

            scores[child_id][co_id] = score

    return scores

# Get all co_id values from the counselor_list
def get_all_counselor_ids():
    query = "SELECT co_id FROM COUNSELOR.counselor_list"
    result = counselordb.execute(query)
    return [row[0] for row in result]  # Use index [0] to access the co_id value

# Calculate average review scores and assign 10 points for scores >= 4.5, 0 points otherwise
def calculate_avg_consulting_scope():
    counselor_ids = get_all_counselor_ids()

    query = """
        SELECT co_id, AVG(consulting_scope) AS avg_consulting_scope
        FROM REVIEW.review_list
        GROUP BY co_id;
    """
    result = review_listdb.execute(query)

    scores = {co_id: 0 for co_id in counselor_ids}  # Initialize scores with 0 for all counselor_ids

    for row in result:
        co_id, avg_consulting_scope = row
        scores[co_id] = 10 if avg_consulting_scope >= 4.0 else 0

    return scores

# 우선순위 매칭
from decimal import Decimal
def calculate_total_rating():
    try:
        # SQL 쿼리
        query = """
            SELECT
                c.child_id,
                cl.co_id,  -- Using counselor_list (cl) to include all counselors
                CASE
                    WHEN COALESCE(SUM(CASE
                        WHEN r.consulting_priority = c.survey_priority_1 THEN 5
                        WHEN r.consulting_priority = c.survey_priority_2 THEN 4
                        WHEN r.consulting_priority = c.survey_priority_3 THEN 3
                        WHEN r.consulting_priority = c.survey_priority_4 THEN 2
                        ELSE 0
                    END), 0) > 10 THEN 30
                    ELSE 0
                END AS total_rating
            FROM
                CHILD_INFO.child_info_list c
            CROSS JOIN (
                SELECT DISTINCT co_id FROM COUNSELOR.counselor_list  -- Using CROSS JOIN to include all counselors
            ) cl
            LEFT JOIN REVIEW.review_list r ON cl.co_id = r.co_id
                                            AND (c.survey_priority_1 = r.consulting_priority
                                                 OR c.survey_priority_2 = r.consulting_priority
                                                 OR c.survey_priority_3 = r.consulting_priority
                                                 OR c.survey_priority_4 = r.consulting_priority)
            GROUP BY
                c.child_id, cl.co_id;
        """

        # 쿼리 실행
        result = child_infodb.execute(query)

        # 결과 출력
        ratings = {}

        for row in result:
            child_id, co_id, total_rating = row

            if child_id not in ratings:
                ratings[child_id] = {}

            ratings[child_id][co_id] = int(total_rating)

        # 결과 반환
        return ratings

    except Exception as e:
        logging.error(f"Error calculating total rating: {e}")
        return None


def combine_scores():
    scores_for_all = calculate_scores_for_all()
    scores_avg_consulting_scope = calculate_avg_consulting_scope()
    total_ratings = calculate_total_rating()

    combined_scores = {}

    for child_id, child_scores in scores_for_all.items():
        combined_scores[child_id] = {}

        for co_id, score_all in child_scores.items():
            # Sum up the scores from all three functions
            score_avg_consulting_scope = scores_avg_consulting_scope.get(co_id, 0)
            total_rating = total_ratings.get(child_id, {}).get(co_id, 0)

            combined_score = score_all + score_avg_consulting_scope + total_rating

            combined_scores[child_id][co_id] = combined_score

    return combined_scores


def display_top_counselors():
    all_combined_scores = combine_scores()

    for child_id, scores in all_combined_scores.items():
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        print(f"\nChild ID: {child_id}")
        print("Top Counselors:")
        for co_id, total_score in sorted_scores:
            # Retrieve counselor information
            query = f"SELECT co_id, co_name, co_consulting FROM COUNSELOR.counselor_list WHERE co_id = {co_id};"
            result = child_infodb.execute(query)  # Use child_infodb connection
            
            # Check if the result is not empty
            if result:
                co_info = result[0]  # Assuming result is a list of tuples, take the first tuple
                co_name, co_consulting = co_info[1], co_info[2]
                print(f"  - Counselor ID: {co_id}, Name: {co_name}, Consulting Areas: {co_consulting}, Total Score: {total_score}")
            else:
                print(f"  - Counselor ID: {co_id}, No information available, Total Score: {total_score}")

# 예시: display_top_counselors() 함수 호출
display_top_counselors()

