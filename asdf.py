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

def Compatibility(user, counselor):
    # 궁합 점수
    MBTI_SCORE=[
        [3, 3, 3, 4, 3, 4, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 3, 4, 3, 4, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 4, 3, 3, 3, 3, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 3, 3, 3, 3, 3, 3, 3, 4, 0, 0, 0, 0, 0, 0, 0],
        [3, 4, 3, 3, 3, 3, 3, 4, 2, 2, 2, 2, 1, 1, 1, 1],
        [4, 3, 3, 3, 3, 3, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 4, 3, 3, 2, 2, 2, 2, 1, 1, 1, 4],
        [3, 3, 4, 3, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1],
        [0, 0, 0, 4, 2, 2, 2, 2, 1, 1, 1, 1, 2, 4, 2, 4],
        [0, 0, 0, 0, 2, 2, 2, 2, 1, 1, 1, 1, 4, 2, 4, 2],
        [0, 0, 0, 0, 2, 2, 2, 2, 1, 1, 1, 1, 2, 4, 2, 4],
        [0, 0, 0, 0, 2, 2, 2, 2, 1, 1, 1, 1, 4, 2, 4, 2],
        [0, 0, 0, 0, 1, 2, 1, 1, 2, 4, 2, 4, 3, 3, 3, 3],
        [0, 0, 0, 0, 1, 2, 1, 1, 4, 2, 4, 2, 3, 3, 3, 3],
        [0, 0, 0, 0, 1, 2, 1, 1, 2, 4, 2, 4, 3, 3, 3, 3],
        [0, 0, 0, 0, 1, 2, 4, 1, 4, 2, 4, 2, 3, 3, 3, 3]
]
    # MBTI 유형
    MBTI = {
        'INFP': 0,
        'ENFP': 1,
        'INFJ': 2,
        'ENFJ': 3,
        'INTJ': 4,
        'ENTJ': 5,
        'INTP': 6,
        'ENTP': 7,
        'ISFP': 8,
        'ESFP': 9,
        'ISTP': 10,
        'ESTP': 11,
        'ISFJ': 12,
        'ESFJ': 13,
        'ISTJ': 14,
        'ESTJ': 15
    }

    # 사용자 MBTI, 상담사 MBTI 궁합
    idx1 = MBTI.get(user)
    idx2 = MBTI.get(counselor)
    if idx1 is not None and idx2 is not None:
        score = MBTI_SCORE[idx1][idx2]
    else:
        score = None
    return score

# Child_info_list 쿼리 실행
query_child = """
SELECT child_id, child_mbti FROM CHILD_INFO.child_info_list
"""
result_child = child_infodb.execute(query_child)

# Counselor_list 쿼리 실행
query_counselor = """
SELECT co_id, co_mbti, co_name FROM COUNSELOR.counselor_list
"""
result_counselor = counselordb.execute(query_counselor)

# Compatibility 함수를 이용하여 Child_mbti와 co_mbti 값의 궁합 점수 확인
for child_id, child_mbti in result_child:
    for co_id, co_mbti, co_name in result_counselor:
        comp_result = Compatibility(child_mbti, co_mbti)
        if comp_result is not None:
            print(f"Child ID: {child_id}, Child MBTI: {child_mbti}, Co ID: {co_id}, Co MBTI: {co_mbti}, Compatibility Score: {comp_result}")
        else:
            print()