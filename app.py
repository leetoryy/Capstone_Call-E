import base64
import logging
from multiprocessing import connection
import traceback
from typing import Counter
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from dbcl import DBconnector
import pymysql
import dbcl
from datetime import datetime, time, timedelta, date
import pytz
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import SocketIO, join_room, leave_room, send
import random
import string
import re

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)

app.secret_key = 'call-e'

# DB 연결 객체 생성
childdb = DBconnector('CHILD')
calledb = DBconnector('CALL_E')
counselordb = DBconnector('COUNSELOR')
child_infodb = DBconnector('CHILD_INFO') #아동mbti, 아동사전설문지 내용, 아동매칭상담사및상담날짜 포함
review_listdb =  DBconnector('REVIEW')
journal_listdb = DBconnector('JOURNAL')
schedule_listdb = DBconnector('COUNSELOR_SCHEDULE')
consulting_listdb = DBconnector('CONSULTING')

AVAILABLE_TIMESLOTS = [
    ("월", "09:00", "10:00"),
    ("월", "10:00", "11:00"),
    ("월", "11:00", "12:00"),
    ("월", "13:00", "14:00"),
    ("월", "14:00", "15:00"),
    ("월", "15:00", "16:00"),
    ("월", "16:00", "17:00"),
    ("화", "09:00", "10:00"),
    ("화", "10:00", "11:00"),
    ("화", "11:00", "12:00"),
    ("화", "13:00", "14:00"),
    ("화", "14:00", "15:00"),
    ("화", "15:00", "16:00"),
    ("화", "16:00", "17:00"),
    ("수", "09:00", "10:00"),
    ("수", "10:00", "11:00"),
    ("수", "11:00", "12:00"),
    ("수", "13:00", "14:00"),
    ("수", "14:00", "15:00"),
    ("수", "15:00", "16:00"),
    ("수", "16:00", "17:00"),
    ("목", "09:00", "10:00"),
    ("목", "10:00", "11:00"),
    ("목", "11:00", "12:00"),
    ("목", "13:00", "14:00"),
    ("목", "14:00", "15:00"),
    ("목", "15:00", "16:00"),
    ("목", "16:00", "17:00"),
    ("금", "09:00", "10:00"),
    ("금", "10:00", "11:00"),
    ("금", "11:00", "12:00"),
    ("금", "13:00", "14:00"),
    ("금", "14:00", "15:00"),
    ("금", "15:00", "16:00"),
    ("금", "16:00", "17:00")
]

# 아동 상담 분야 가져오기
def get_all_child_survey_consulting():
    query = f"SELECT child_id, survey_consulting FROM CHILD_INFO.child_info_list "
    result = child_infodb.execute(query)
    
    return result

# 상담사 상담 분야 가져오기
def get_all_counselor_survey_consulting():
    query = "SELECT co_id, co_consulting, co_name FROM COUNSELOR.counselor_list"
    result = counselordb.execute(query)
    return result

# HTML 렌더링을 위한 기본 경로
@app.route('/',methods=['GET','POST'])
def index():
    return render_template('counselor/join.html')
    
#아이디 패스워드 검사
def authenticate_child(child_ID, child_pw):
    query = f"SELECT COUNT(*) FROM CHILD.child_list WHERE child_id = '{child_ID}' AND child_password = '{child_pw}'"
    result = childdb.execute(query)
    return result and result[0][0] == 1

def authenticate_counselor(counselor_ID, counselor_pw):
    query = f"SELECT COUNT(*), co_name FROM COUNSELOR.counselor_list WHERE co_id = '{counselor_ID}' AND co_password = '{counselor_pw}'"
    result = counselordb.execute(query)
    return result and result[0][0] == 1, result[0][1] if result else None

# MBTI 궁합
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'child':
            child_ID = request.form.get('ch_id2')
            child_pw = request.form.get('ch_pw_2')
            
            try:
                # SQL 쿼리 작성
                sql = "SELECT child_name FROM child_list WHERE child_id = %s"
    
                # 쿼리 실행
                result = childdb.query(sql, (child_ID,))
                
                if result:
                    child_name = result[0][0]
                    print("냥",child_name)
                
                    if authenticate_child(child_ID, child_pw):
                        print("성공")
                        session['child_name'] = child_name
                        session['child_id'] = child_ID
                        
                        session[child_ID] = {'logged_in': True, 'child_name':child_name}
                        print(session[child_ID])
                        return jsonify({'user_type': 'child', 'child_id': child_ID})

                    else:
                        print("실패")
                        return "아이디 또는 비밀번호가 일치하지 않습니다."

            except Exception as e:
                print(f"Error: {e}")
                return "로그인 중 오류가 발생했습니다."

        elif user_type == 'counselor':
            counselor_ID = request.form.get('co_id2')
            counselor_pw = request.form.get('co_pw_2')

            try:
                auth_result, counselor_name = authenticate_counselor(counselor_ID, counselor_pw)
                
                if auth_result:
                    # 로그인 성공 시 세션에 상담사 이름 저장
                    session['counselor_name'] = counselor_name
                    session['co_id'] = counselor_ID
                    session[counselor_ID] = {'logged_in': True}
                    print(session[counselor_ID])
                    return jsonify({'user_type': 'counselor', 'counselor_name': counselor_name, 'counselor_ID': counselor_ID})
                    
                else:
                    print("실패")
                    return "아이디 또는 비밀번호가 일치하지 않습니다."

            except Exception as e:
                print(f"Error: {e}")
                return "로그인 중 오류가 발생했습니다."


# 전화번호 포맷팅 함수
def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    if len(digits) == 11:
        formatted_number = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    else:
        formatted_number = phone_number
    
    return formatted_number

@app.route('/join', methods=['GET', 'POST'])
def join_html():
    error_message = None

    if request.method == 'POST':
        user_type = request.form.get('user_type')

        if user_type == 'child':
            # 아동 회원가입 처리
            childName = request.form.get('ch_name')
            childId = request.form.get('ch_id')
            childPassword = request.form.get('ch_pw')
            childPhoneNum = format_phone_number(request.form.get('ch_ph'))
            childEmail = request.form.get('ch_email')
            childBirthYear = request.form.get('ch_by')
            childBirthMonth = request.form.get('ch_bm')
            childBirthDay = request.form.get('ch_bd')
            childAddress = request.form.get('ch_address')
            parentName = request.form.get('pa_name')
            
            # 받은 값 출력 또는 로깅
            print("아동 폼 값:")
            print(f"childName: {childName}")
            print(f"childId: {childId}")
            print(f"childPassword: {childPassword}")
            print(f"childPhoneNum: {childPhoneNum}")
            print(f"childEmail: {childEmail}")
            print(f"childBirthYear: {childBirthYear}")
            print(f"childBirthMonth: {childBirthMonth}")
            print(f"childBirthDay: {childBirthDay}")
            print(f"childAddress: {childAddress}")
            print(f"parentName: {parentName}")
            
            try:
                birth_date_string = f"{childBirthYear}{childBirthMonth.zfill(2)}{childBirthDay.zfill(2)}"
                birth_date_int = int(birth_date_string)

                insert_query = f"""
                    INSERT INTO CHILD.child_list (child_name, child_id, child_password, parent_phone, parent_email,
                                    child_birth, child_address, parent_name)
                    VALUES ('{childName}', '{childId}', '{childPassword}', '{childPhoneNum}', '{childEmail}',
                            {birth_date_int}, '{childAddress}', '{parentName}');
                """

                childdb.insert(insert_query)
            
                print(f"Query: {insert_query}")
                print(childId)
                return jsonify({'user_type': 'child', 'child_id': childId, 'parent_name': parentName})
                
            except Exception as e:
                error_message = '회원 가입 중 오류가 발생했습니다.'
                print(f"Error Type: {type(e)}")
                print(f"Error Details: {e.args}")
                 
        elif user_type == 'counselor':
            # 상담사 회원가입 처리
            counselorName = request.form.get('co_name')
            counselorID = request.form.get('co_id')
            counselorPassword = request.form.get('co_pw')
            counselorPhone = format_phone_number(request.form.get('co_phone'))
            counselorEmail = request.form.get('co_email')
            counselorBirthYear = request.form.get('co_birth_year')
            counselorBirthMonth = request.form.get('co_birth_month')
            counselorBirthDay = request.form.get('co_birth_day')
            mbti = request.form.get('mbti')
            areas_raw = request.form.get('areas')
            areas = areas_raw.split(',') if areas_raw else []

            # 받은 값 출력 또는 로깅
            print("상담사 폼 값:")
            print(f"counselorName: {counselorName}")
            print(f"counselorID: {counselorID}")
            print(f"counselorPassword: {counselorPassword}")
            print(f"counselorPhone: {counselorPhone}")
            print(f"counselorEmail: {counselorEmail}")
            print(f"counselorBirthYear: {counselorBirthYear}")
            print(f"counselorBirthMonth: {counselorBirthMonth}")
            print(f"counselorBirthDay: {counselorBirthDay}")
            print(f"mbti: {mbti}")
            print(f"areas: {areas}")

            try:
                birth_date_string = f"{counselorBirthYear}{counselorBirthMonth.zfill(2)}{counselorBirthDay.zfill(2)}"
                birth_date_int = int(birth_date_string)
                

                insert_query = f"""
                    INSERT INTO COUNSELOR.counselor_list (co_name, co_id, co_password, co_phone, co_email,
                    co_birth, co_consulting, co_mbti)
                    VALUES ('{counselorName}', '{counselorID}', '{counselorPassword}', '{counselorPhone}', '{counselorEmail}',
                    {birth_date_int}, '{', '.join(areas)}', '{mbti}');
                """

                counselordb.insert(insert_query)
                print(f"Query: {insert_query}")
                return jsonify({'user_type': 'counselor'})

            except Exception as e:
                error_message = f'회원 가입 중 오류가 발생했습니다: {e}'
                print(f"Error Type: {type(e)}")
                print(f"Error Details: {e}")
                
    return render_template('counselor/join.html')


# ID 중복 확인을 위한 엔드포인트
@app.route('/check_id_duplicate', methods=['POST'])
def check_id_duplicate():
    try:
        # 클라이언트로부터 전달된 아이디를 JSON 형식으로 받음
        data = request.get_json()
        child_id = data.get('child_id', None)

        if not child_id:
            raise ValueError("No child_id provided")

        # 데이터베이스에서 아이디 중복 확인
        query = f"SELECT COUNT(*) FROM CHILD.child_list WHERE child_id = '{child_id}'"
        result = childdb.fetch_one(query)

        # 디버깅: 쿼리와 결과 확인
        print(f"Query: {query}")
        print(f"Query result: {result}")

        if result is None:
            raise Exception(f"Query returned no result for child_id '{child_id}'")

        # 결과를 JSON 형식으로 반환
        is_duplicate = result[0] > 0
        return jsonify({"query_result": result, "duplicate": is_duplicate})

    except Exception as e:
        # 오류 처리
        print(f"Error checking ID duplicate: {e}")
        return jsonify({"query_result": None, "duplicate": False, "error": str(e)})
    
 # 회원가입할 때 사번과 이름이 일치하는지 확인   
@app.route('/check_name_and_id_association', methods=['POST'])
def check_name_and_id_association():
    try:
        counselor_name = request.form.get('counselor_name')
        counselor_id = request.form.get('counselor_id')

        # 주어진 counselor_name이 counselor_id와 연관되어 있는지 확인
        query_name_check = f"SELECT COUNT(*) FROM CALL_E.coworker_list WHERE co_name = '{counselor_name}' AND co_id = {counselor_id}"
        result_name_check = calledb.execute(query_name_check)

        # 주어진 counselor_id가 counselor_name과 연관되어 있는지 확인
        query_id_check = f"SELECT COUNT(*) FROM CALL_E.coworker_list WHERE co_name = '{counselor_name}' AND co_id = {counselor_id}"
        result_id_check = calledb.execute(query_id_check)

        if result_name_check and result_id_check:
            return jsonify({
                "name_associated_with_id": result_name_check[0][0] > 0,
                "id_associated_with_name": result_id_check[0][0] > 0
            })
        raise Exception("쿼리 실행 중 오류 발생.")

    except Exception as e:
        print(f"이름과 사번 연관성 확인 중 오류: {e}")
        return jsonify({"error": str(e)})

def get_consultation_status(start_time, end_time):
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    current_time = now.time()

    if start_time <= current_time <= end_time:
        return '상담 중'
    elif current_time < start_time:
        return '상담 대기'
    else:
        return '상담 완료'

def timedelta_to_time(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return time(hours, minutes, seconds)

@app.route('/counselor_home_data')
def counselor_home_data():
    co_id = session.get('co_id', '')

    if not co_id:
        return jsonify({"error": "No counselor ID found in session"}), 400

    query = """
    SELECT ci.child_name, ci.child_mbti, ci.survey_consulting, ci.co_id, cd.parent_phone, 
           sl.start_time, sl.end_time, sl.day_of_week, sl.consultation_code
    FROM CHILD_INFO.child_info_list ci
    JOIN CHILD.child_list cd ON ci.child_id = cd.child_id
    JOIN COUNSELOR_SCHEDULE.schedule_list sl ON ci.child_id = sl.child_id
    WHERE ci.co_id = %s
    """
    with child_infodb.get_cursor() as cursor:
        cursor.execute(query, (co_id,))
        results = cursor.fetchall()

    # 현재 요일을 한글 형식으로 변환
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    today_weekday = now.strftime('%a')
    weekday_map = {
        'Mon': '월',
        'Tue': '화',
        'Wed': '수',
        'Thu': '목',
        'Fri': '금',
        'Sat': '토',
        'Sun': '일'
    }
    today_weekday_kr = weekday_map[today_weekday]

    data = []
    for row in results:
        child_name, child_mbti, survey_consulting, co_id, parent_phone, start_time_td, end_time_td, day_of_week, consultation_code = row
        
        # `timedelta`를 `time` 객체로 변환
        start_time = timedelta_to_time(start_time_td)
        end_time = timedelta_to_time(end_time_td)
        
        if day_of_week == today_weekday_kr:
            status = get_consultation_status(start_time, end_time)
            data.append({
                'name': child_name,
                'mbti': child_mbti,
                'type': survey_consulting,
                'status': status,
                'contact': parent_phone,
                'code': consultation_code
            })

    return jsonify(data)

@app.route('/counselor_today_data')
def counselor_today_data():
    co_id = session.get('co_id', '')

    if not co_id:
        return jsonify({"error": "No counselor ID found in session"}), 400

    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    today_weekday = now.strftime('%a')
    weekday_map = {
        'Mon': '월',
        'Tue': '화',
        'Wed': '수',
        'Thu': '목',
        'Fri': '금',
        'Sat': '토',
        'Sun': '일'
    }
    today_weekday_kr = weekday_map[today_weekday]

    query = """
    SELECT ci.child_name, sl.start_time, sl.end_time, sl.day_of_week
    FROM CHILD_INFO.child_info_list ci
    JOIN CHILD.child_list cd ON ci.child_id = cd.child_id
    JOIN COUNSELOR_SCHEDULE.schedule_list sl ON ci.child_id = sl.child_id
    WHERE ci.co_id = %s
    """
    with child_infodb.get_cursor() as cursor:
        cursor.execute(query, (co_id,))
        results = cursor.fetchall()

    today_data = []
    for row in results:
        child_name, start_time_td, end_time_td, day_of_week = row
        
        start_time = timedelta_to_time(start_time_td)
        end_time = timedelta_to_time(end_time_td)

        if day_of_week == today_weekday_kr:
            today_data.append({
                'name': child_name,
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M')
            })

    return jsonify(today_data)


def recently_journal(co_id):
    korea_timezone = pytz.timezone('Asia/Seoul')
    current_date = datetime.now(korea_timezone).date()
    
    query = """
    SELECT jl.co_id, jl.child_id, jl.consulting_day, jl.consulting_title, cl.child_name, cl.survey_consulting 
    FROM journal_list jl 
    JOIN CHILD_INFO.child_info_list cl ON cl.child_id = jl.child_id 
    WHERE cl.co_id = %s
    AND jl.consulting_day >= DATE_SUB(%s, INTERVAL 7 DAY)
    AND jl.consulting_day <= %s
    """
    recent_journals = journal_listdb.query(query, (co_id, current_date, current_date))
    
    # 튜플을 딕셔너리 형태로 변환
    recent_journals = [
        {
            'co_id': row[0],
            'child_id': row[1],
            'consulting_day': row[2],
            'consulting_title': row[3],
            'child_name': row[4],
            'survey_consulting': row[5]
        }
        for row in recent_journals
    ]
    
    print(recent_journals)
    return recent_journals

def recently_review(co_id):
    korea_timezone = pytz.timezone('Asia/Seoul')
    current_date = datetime.now(korea_timezone).date()
    
    query = """
    SELECT rl.co_id, rl.child_id, rl.consulting_day, rl.consulting_scope, rl.consulting_etc, cl.child_name
    FROM REVIEW.review_list rl 
    JOIN CHILD_INFO.child_info_list cl ON cl.child_id = rl.child_id 
    WHERE cl.co_id = %s
    AND rl.consulting_day >= DATE_SUB(%s, INTERVAL 7 DAY)
    AND rl.consulting_day <= %s
    """
    recent_reviews = review_listdb.query(query, (co_id, current_date, current_date))
    
    recent_reviews = [
        {
            'co_id': row[0],
            'child_id': row[1],
            'consulting_day': row[2],
            'consulting_scope': row[3],
            'consulting_etc': row[4],  
            'child_name': row[5]       
        }
        for row in recent_reviews
    ]
    
    print(recent_reviews)
    return recent_reviews

@app.route('/counselor_home')
def counselor_home_html():
    counselor_name = request.args.get('counselor_name', '')
    co_id = session.get('co_id', '')
    
    recent_journals = recently_journal(co_id)
    recent_reviews = recently_review(co_id)
    return render_template('counselor/counselor_home.html', counselor_name=counselor_name, recent_journals=recent_journals, recent_reviews=recent_reviews)


@app.route('/child_list')
def child_list():
    try:
        query = """
            SELECT 
                ci.child_name, 
                ci.child_id, 
                ci.child_mbti, 
                ci.survey_consulting, 
                co.co_name, 
                cd.parent_name, 
                cd.parent_phone
            FROM 
                CHILD_INFO.child_info_list ci
            JOIN 
                CHILD.child_list cd ON ci.child_id = cd.child_id 
            LEFT JOIN 
                COUNSELOR.counselor_list co ON ci.co_id = co.co_id;
        """
        child_info_data = child_infodb.query(query)
        keys = ['child_name', 'child_id', 'child_mbti', 'survey_consulting', 'co_name', 'parent_name', 'parent_phone']
        child_info_data_dicts = [convert_to_dict(keys, row) for row in child_info_data]
        
        return render_template('counselor/child_list.html', child_info_data=child_info_data_dicts)
    except Exception as e:
        logging.error(f"Error fetching child list: {str(e)}")
        return render_template('counselor/child_list.html', child_info_data=[])

def convert_to_dict(keys, values):
    return {keys[i]: values[i] for i in range(len(keys))}

@app.route('/counsel_child_list')
def counsel_child_list():
    try:
        counselor_id = session.get('co_id', '')
        
        query = """
            SELECT 
                ci.child_name, 
                ci.child_id, 
                ci.child_mbti, 
                ci.survey_consulting, 
                co.co_name, 
                cd.parent_name, 
                cd.parent_phone
            FROM 
                CHILD_INFO.child_info_list ci
            JOIN 
                CHILD.child_list cd ON ci.child_id = cd.child_id 
            LEFT JOIN 
                COUNSELOR.counselor_list co ON ci.co_id = co.co_id
            WHERE 
                co.co_id = %s;
        """
        child_info_data = child_infodb.query(query, (counselor_id,))
        keys = ['child_name', 'child_id', 'child_mbti', 'survey_consulting', 'co_name', 'parent_name', 'parent_phone']
        child_info_data_dicts = [convert_to_dict(keys, row) for row in child_info_data]
        
        return render_template('counselor/counsel_child_list.html', child_info_data=child_info_data_dicts)
    except Exception as e:
        logging.error(f"Error fetching child list: {str(e)}")
        return render_template('counselor/counsel_child_list.html', child_info_data=[])

@app.route('/get_children_by_date', methods=['GET'])
def get_children_by_date():
    co_id = session.get('co_id', '')
    
    query = """
    SELECT cl.child_id, cl.consulting_day, ci.child_name  
    FROM CONSULTING.consulting_list cl 
    JOIN CHILD_INFO.child_info_list ci ON cl.child_id = ci.child_id 
    WHERE cl.co_id = %s
    """
    children = childdb.query(query, (co_id,))
    
    children_list = []
    for child in children:
        children_list.append((child[0], child[1].strftime('%Y-%m-%d'), child[2]))
    
    return jsonify(children=children_list, ensure_ascii=False)

@app.route('/get_child_details', methods=['GET'])
def get_child_details():
    child_id = request.args.get('child_id')
    query = """
    SELECT ci.survey_consulting, ci.child_mbti, ci.survey_priority_1, ci.survey_priority_2, ci.survey_priority_3, ci.survey_priority_4 
    FROM CHILD_INFO.child_info_list ci 
    WHERE ci.child_id = %s
    """
    child_details = child_infodb.query(query, (child_id,))
    
    child_details_dict = {
        "survey_consulting": child_details[0][0],
        "child_mbti": child_details[0][1],
        "survey_priority_1": child_details[0][2],
        "survey_priority_2": child_details[0][3],
        "survey_priority_3": child_details[0][4],
        "survey_priority_4": child_details[0][5]
    }
    
    return jsonify(child_details_dict)

@app.route('/save_journal', methods=['POST'])
def save_journal():
    co_id = session.get('co_id', '')
    
    child_id = request.form['child-id']
    consulting_day = request.form['counsel-date']
    consulting_content = request.form['counsel-content']
    consulting_result = request.form['counsel-result']
    consulting_title = request.form['counsel-title']
    
    select_query = f"""
    SELECT co_id, child_id, consulting_day
    FROM CONSULTING.consulting_list
    WHERE child_id='{child_id}' AND consulting_day='{consulting_day}' AND co_id='{co_id}';
    """
    consulting_data = consulting_listdb.execute(select_query)

    if consulting_data:
        check_journal_query = f"""
        SELECT *
        FROM JOURNAL.journal_list
        WHERE child_id='{child_id}' AND consulting_day='{consulting_day}' AND co_id='{co_id}';
        """
        journal_data = journal_listdb.execute(check_journal_query)
        
        if journal_data:
            return jsonify(message="이미 등록된 상담일지 입니다."), 400
        else:
            insert_query = f"""
            INSERT INTO JOURNAL.journal_list (child_id, co_id, consulting_day, consulting_content, consulting_result, consulting_title)
            VALUES ('{child_id}', '{co_id}', '{consulting_day}', '{consulting_content}', '{consulting_result}', '{consulting_title}');
            """

            journal_listdb.insert(insert_query)
            return jsonify(message="상담일지가 저장되었습니다."), 200
    else:

        return jsonify(message="No matching consulting data found"), 404
    
@app.route('/counsel_write') 
def counsel_write_html():
    co_id = session.get('co_id', '')
    return render_template('counselor/counsel_write.html')


@app.route('/counsel_view_data')
def get_counsel_view_data():
    co_id = session.get('co_id', '')
    if not co_id:
        return jsonify({"error": "Counselor ID not found in session"}), 400

    query = """
    SELECT jl.co_id, jl.child_id, jl.consulting_day, jl.consulting_title, cl.child_name, cl.survey_consulting
    FROM JOURNAL.journal_list jl 
    JOIN CHILD_INFO.child_info_list cl ON cl.child_id = jl.child_id 
    WHERE jl.co_id = %s
    """
    
    try:
        rows = journal_listdb.query(query, (co_id,))
        result = []
        for row in rows:
            result.append({
                "co_id": row[0],
                "child_id": row[1],
                "consulting_day": row[2].strftime("%Y-%m-%d"),
                "consulting_title": row[3],
                "child_name": row[4],
                "survey_consulting": row[5]
            })
        return jsonify(result)
    except Exception as e:
        logging.error("Failed to fetch data from database", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/counsel_view') 
def counsel_view_html():
    co_id = session.get('co_id', '')
    return render_template('counselor/counsel_view.html')

@app.route('/update_journal', methods=['POST'])
def update_journal():
    try:
        co_id = session.get('co_id', '')
        if not co_id:
            return jsonify({"error": "Counselor ID not found in session"}), 400
        
        child_id = request.form['child-id']
        consulting_day = request.form['counsel-date']
        consulting_content = request.form.get('counsel-content')
        consulting_result = request.form.get('counsel-result')
        consulting_title = request.form.get('counsel-title')
        
        update_fields = []
        
        if consulting_content:
            update_fields.append(f"consulting_content='{consulting_content}'")
        
        if consulting_result:
            update_fields.append(f"consulting_result='{consulting_result}'")
        
        if consulting_title:
            update_fields.append(f"consulting_title='{consulting_title}'")
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        update_query = f"UPDATE JOURNAL.journal_list SET {', '.join(update_fields)} WHERE child_id='{child_id}' AND consulting_day='{consulting_day}' AND co_id='{co_id}'"
                
        journal_listdb.update(update_query)
        
        return jsonify(message="상담일지가 수정되었습니다."), 200
    except Exception as e:
        logging.error("Failed to update journal", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/counsel_view_edit')
def counsel_view_edit():
    co_id = session.get('co_id', '')
    child_id = request.args.get('child_id')
    consulting_day = request.args.get('consulting_day')
    
    query = """
    SELECT jl.consulting_title, jl.consulting_content, jl.consulting_result, 
           ci.child_name, ci.survey_consulting, ci.child_mbti, ci.survey_priority_1, 
           ci.survey_priority_2, ci.survey_priority_3, ci.survey_priority_4 
    FROM JOURNAL.journal_list jl 
    JOIN CHILD_INFO.child_info_list ci ON jl.child_id = ci.child_id 
    WHERE jl.child_id = %s AND jl.consulting_day = %s
    """
    
    journal_data = journal_listdb.query(query, (child_id, consulting_day))
    
    if journal_data:
        journal_data = journal_data[0]
        context = {
            'consulting_title': journal_data[0],
            'consulting_content': journal_data[1],
            'consulting_result': journal_data[2],
            'child_name': journal_data[3],
            'survey_consulting': journal_data[4],
            'child_mbti': journal_data[5],
            'survey_priority_1': journal_data[6],
            'survey_priority_2': journal_data[7],
            'survey_priority_3': journal_data[8],
            'survey_priority_4': journal_data[9],
            'child_id': child_id,
            'consulting_day': consulting_day
        }
        return render_template('counselor/counsel_view_edit.html', **context)
    else:
        return "No data found", 404

@app.route('/counsel_schedule')
def counsel_schedule_html():
    co_id = session.get('co_id', '')
    if not co_id:
        return redirect(url_for('login'))  # 세션에 상담사 ID가 없는 경우 로그인 페이지로 리디렉션
    
    # 데이터베이스에서 상담사 일정 가져오기
    query = """
        SELECT cl.child_name, sl.day_of_week, sl.start_time, sl.end_time
        FROM COUNSELOR_SCHEDULE.schedule_list sl
        JOIN CHILD_INFO.child_info_list cl ON cl.child_id = sl.child_id
        WHERE sl.co_id = %s
    """
    schedule_data = schedule_listdb.query(query, (co_id,))
    
    # 가져온 데이터 콘솔에 출력
    print("Schedule Data:", schedule_data)
    
    # 데이터를 JSON 형식으로 변환
    schedule_events = []
    for entry in schedule_data:
        start_time = timedelta_to_str(entry[2])
        end_time = timedelta_to_str(entry[3])
        event = {
            'title': f"{start_time} ~ {end_time} {entry[0]} 아동",  # 시작 시간 ~ 종료 시간 - 아동 이름
            'daysOfWeek': [convert_day_to_number(entry[1])],  # day_of_week
            'startTime': start_time,  # start_time
            'endTime': end_time,  # end_time
            'display': 'block'  # 시간 정보를 표시하지 않도록 설정
        }
        schedule_events.append(event)
    
    # 변환된 데이터 콘솔에 출력
    print("Schedule Events:", schedule_events)
    
    return render_template('counselor/counsel_schedule.html', schedule_events=schedule_events)

def convert_day_to_number(day_of_week):
    days = {
        '일': 0,
        '월': 1,
        '화': 2,
        '수': 3,
        '목': 4,
        '금': 5,
        '토': 6
    }
    return days.get(day_of_week, 0)

def timedelta_to_str(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"


@app.route('/counsel_counseling') 
def counsel_counseling_html():
    try:
        # 데이터베이스에서 child_id 가져오기
        query = "SELECT child_id FROM CHILD.child_list;"
        child_ids = childdb.execute(query)
        print(child_ids)
        return render_template('counselor/counsel_counseling.html',child_ids=child_ids)

    except Exception as e:
        # 예외 처리
        return "An error occurred: " + str(e)
    return render_template('counselor/counsel_counseling.html')

@app.route('/survey_pre',  methods=[ 'GET','POST'])
def survey_pre_html():
    child_id = request.args.get('child_id', default=None)
    parent_name = request.args.get('parent_name', default=None)
    if request.method == 'POST':
        # 폼이 제출된 경우에만 처리
        child_id = request.form.get('childID', default=None)
        parent_name = request.form.get('guardianName', default=None)
        priority1 = request.form.get('paymentMethod1', default=None)
        priority2 = request.form.get('paymentMethod2', default=None)
        priority3 = request.form.get('paymentMethod3', default=None)
        priority4 = request.form.get('paymentMethod4', default=None)
        subject = request.form.get('paymentMethod', default=None)
        medicine_name = request.form.get('medicineName', default=None)
        additional_notes = request.form.get('additionalNotes', default=None)

        # 데이터를 출력
        print("Child ID:", child_id)
        print("Parent Name:", parent_name)
        print("Priority 1:", priority1)
        print("Priority 2:", priority2)
        print("Priority 3:", priority3)
        print("Priority 4:", priority4)
        print("Subject:", subject)
        print("Medicine Name:", medicine_name)
        print("Additional Notes:", additional_notes)
        
        try:
            # child_id를 사용하여 child_name 조회
            child_name = childdb.fetch_one(f"SELECT child_name FROM CHILD.child_list WHERE child_id = '{child_id}'")

            # CHILD_INFO.child_info_list에 데이터 삽입
            insert_query = f"""
                INSERT INTO CHILD_INFO.child_info_list (child_id, child_name, survey_priority_1, survey_priority_2,
                    survey_priority_3, survey_priority_4, survey_consulting, survey_diagnosis, survey_etc)
                VALUES ('{child_id}', '{child_name}', '{priority1}', '{priority2}', '{priority3}', '{priority4}',
                        '{subject}', '{medicine_name}', '{additional_notes}');
            """            
            child_infodb.insert(insert_query)
            print(f"Query: {insert_query}")
            
            return render_template('user/mbti_home.html')
                
        except Exception as e:
            error_message = '오류가 발생했습니다.'
            print(f"Error Type: {type(e)}")
            print(f"Error Details: {e.args}")
                
    return render_template('user/survey_pre.html', child_id=child_id, parent_name=parent_name)

@app.route('/survey_pre_edit', methods=['GET', 'POST'])
def survey_pre_edit_html():
    child_id = session.get('child_id')
    if request.method == 'POST':
        # 폼이 제출된 경우에만 처리
        child_name = request.form.get('childName', default=None)
        parent_name = request.form.get('guardianName', default=None)
        priority1 = request.form.get('paymentMethod1', default=None)
        priority2 = request.form.get('paymentMethod2', default=None)
        priority3 = request.form.get('paymentMethod3', default=None)
        priority4 = request.form.get('paymentMethod4', default=None)
        subject = request.form.get('paymentMethod', default=None)
        medicine_name = request.form.get('medicineName', default=None)
        additional_notes = request.form.get('additionalNotes', default=None)

        try:
            # CHILD_INFO.child_info_list에 데이터 업데이트
            update_query = f"""
                UPDATE CHILD_INFO.child_info_list
                SET child_name='{child_name}', survey_priority_1='{priority1}', survey_priority_2='{priority2}', 
                    survey_priority_3='{priority3}', survey_priority_4='{priority4}', survey_consulting='{subject}', 
                    survey_diagnosis='{medicine_name}', survey_etc='{additional_notes}'
                WHERE child_id='{child_id}';
            """
            child_infodb.insert(update_query)
             # JSON 응답 반환
             
            return jsonify(message="상담일지가 수정되었습니다."), 200
        except Exception as e:
            logging.error("Failed to update survey", exc_info=True)
            return jsonify({"error": str(e)}), 500
                       
    # 데이터베이스에서 아동 이름과 보호자 성함을 각각 가져옴
    child_name_result = childdb.fetch_one(f"SELECT child_name FROM CHILD.child_list WHERE child_id = '{child_id}'")
    parent_name_result = childdb.fetch_one(f"SELECT parent_name FROM CHILD.child_list WHERE child_id = '{child_id}'")

    # 반환 값이 문자열로 가정하고 그대로 할당
    child_name = child_name_result if child_name_result else ""
    parent_name = parent_name_result if parent_name_result else ""

    return render_template('user/survey_pre_edit.html', child_id=child_id, child_name=child_name, parent_name=parent_name)

@app.route('/counsel_review') 
def counsel_review_html():
    co_id = session.get('co_id')
    query = """
        SELECT
            cl.child_name,
            r.consulting_day,
            r.consulting_scope,
            r.consulting_etc
        FROM
            REVIEW.review_list r
        JOIN
            CHILD.child_list cl ON r.child_id = cl.child_id
        WHERE
            r.co_id = %s;       
    """
    result = review_listdb.execute(query,(co_id))
    child_name = result[0][0]
    consulting_day = result[0][1]
    consulting_scope = result[0][2]
    consulting_etc = result[0][3]
    
    reviews =[
        {
            'child_name' : row[0],
            'consulting_day' : row[1],
            'consulting_scope' : row[2],
            'consulting_etc' : row[3]
        }
        for row in result
    ]
    
    return render_template('counselor/counsel_review.html',reviews=reviews)

@app.route('/counsel_review_search')
def counsel_review_search():
    date = request.args.get('date')
    name = request.args.get('name')
    co_id = session.get('co_id', None)  

    base_query = """
        SELECT
            cl.child_name,
            r.consulting_day,
            r.consulting_scope,
            r.consulting_etc
        FROM
            REVIEW.review_list r
        JOIN
            CHILD.child_list cl ON r.child_id = cl.child_id
        WHERE
            r.co_id = %s
    """

    conditions = []
    params = [co_id]  # 초기 파라미터로 co_id 설정

    if date:
        conditions.append("r.consulting_day = %s")
        params.append(date)  # 날짜 파라미터 추가
    if name:
        conditions.append("cl.child_name LIKE %s")
        params.append(name)  # 이름 파라미터 추가

    if conditions:
        query = base_query + " AND " + " AND ".join(conditions)
    else:
        query = base_query

    print("최종 쿼리:", query)
    print("사용된 파라미터:", params)

    # 데이터베이스 쿼리 실행
    review_listdb = DBconnector('REVIEW')
    result = review_listdb.query(query, params)
    print("리뷰 검색 결과:", result)

    # 결과를 JSON으로 변환
    reviews = [
        {
            'child_name': row[0],
            'consulting_day': row[1].strftime('%Y-%m-%d'),
            'consulting_scope': row[2],
            'consulting_etc': row[3]
        }
        for row in result
    ]
    return jsonify(reviews)




@app.route('/user_home')
def user_home_html():
    return render_template('user/user_home.html')

@app.route('/mbti_home')
def mbti_home_html():
    return render_template('user/mbti_home.html')

@app.route('/user_counsel_view_data')
def get_user_counsel_view_data():
    child_id = session.get('child_id','')
    if not child_id:
        return jsonify({"error": "Counselor ID not found in session"}), 400
    
    query = """
    SELECT jl.consulting_title , cl.co_name , jl.consulting_day  , jl.consulting_content , jl.consulting_result
    FROM JOURNAL.journal_list jl 
    JOIN COUNSELOR.counselor_list cl ON jl.co_id = cl.co_id 
    WHERE jl.child_id  = %s
    """ 
    
    try:
        rows = journal_listdb.query(query, (child_id,))
        user_counsel_view = []
        for row in rows:
            user_counsel_view.append({
            "consulting_title": row[0],
            "co_name": row[1],
            "consulting_day": row[2],
            "consulting_content": row[3],
            "consulting_result": row[4]
            })
        return jsonify(user_counsel_view)
    except Exception as e:
        logging.error("Failed to fetch data from database", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/user_counsel_view')
def user_counsel_view_html():
    child_id = session.get('child_id')    
    return render_template('user/user_counsel_view.html')

@app.route('/user_review')
def user_review_html():
    return render_template('user/user_review.html')

@app.route('/user_review_detail') 
def user_review_detail_html():
    return render_template('user/user_review_ detail.html')

# 상담사 상담 분야 가져오기
def get_counselor_consulting():
    query = "SELECT co_id, co_consulting FROM COUNSELOR.counselor_list"
    result = counselordb.execute(query)
    return result

# child_id 별로 모든 상담사와의 일치 여부를 확인하여 점수 부여
def calculate_scores_for_all():
    child_survey_consulting = get_all_child_survey_consulting()
    counselor_survey_consulting = get_counselor_consulting()

    scores = {}

    for child_row in child_survey_consulting:
        child_id, child_consulting = child_row

        scores[child_id] = {}

        for co_id, co_consulting in counselor_survey_consulting:
            score = 40 if all(survey_consulting in co_consulting.split(', ') for survey_consulting in
                              child_consulting.split(', ')) else 0
            scores[child_id][co_id] = score

    return scores

#리뷰 점수 부여, 평균 점수 4.0 이상이면 10점
def get_all_counselor_ids():
    query = "SELECT co_id FROM COUNSELOR.counselor_list"
    result = counselordb.execute(query)
    return [row[0] for row in result]  


def calculate_avg_consulting_scope():
    counselor_ids = get_all_counselor_ids()

    query = """
        SELECT co_id, AVG(consulting_scope) AS avg_consulting_scope
        FROM REVIEW.review_list
        GROUP BY co_id;
    """
    result = review_listdb.execute(query)

    scores = {co_id: 0 for co_id in counselor_ids}  

    for row in result:
        co_id, avg_consulting_scope = row
        scores[co_id] = 10 if avg_consulting_scope >= 4.0 else 0

    return scores

# 우선순위 매칭
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



def get_best_match_counselors(child_id):
    # 아동의 MBTI 가져오기
    child_mbti_query = f"""
        SELECT child_mbti
        FROM CHILD_INFO.child_info_list
        WHERE child_id = '{child_id}';
    """
    child_mbti_result = child_infodb.execute(child_mbti_query)
    child_mbti = child_mbti_result[0][0] if child_mbti_result else None
    
    if not child_mbti:
        return []

    # 상담사 정보 및 평균 점수 가져오기
    counselor_query = """
        SELECT
            co.co_id,
            co.co_name,
            co.co_mbti,
            co.co_consulting,
            IFNULL(AVG(r.consulting_scope), 0) AS avg_scope,
            GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority) AS priorities
        FROM COUNSELOR.counselor_list co
        LEFT JOIN REVIEW.review_list r ON co.co_id = r.co_id
        GROUP BY co.co_id, co.co_name, co.co_mbti, co.co_consulting
        ORDER BY co.co_id;
    """
    counselor_rows = counselordb.execute(counselor_query)
    counselors = [
        (row[0], row[1], row[2], row[3], row[4], row[5])
        for row in counselor_rows
    ]

    # 궁합표에 따른 추가 점수 계산 및 튜플에 추가
    best_mbti_matches = {
        'INFP': ['ENFJ', 'ENTJ'],
        'ENFP': ['ENFJ', 'ENTJ'],
        'INFJ': ['ENFP', 'ENTP'],
        'ENFJ': ['ENFP', 'ENTJ', 'ENTP'],
        'INTJ': ['ISTP', 'ESTP'],
        'ENTJ': ['ISTP', 'ESTP'],
        'INTP': ['ISTP', 'ESTP'],
        'ENTP': ['ESTP'],
        'ISFP': ['ISTP', 'ESTP'],
        'ESFP': ['ISTP', 'ESTP'],
        'ISTP': ['ISTP', 'ESTP'],
        'ESTP': ['ISTP', 'ESTP'],
        'ISFJ': ['ISTP', 'ESTP'],
        'ESFJ': ['ISTP', 'ESTP'],
        'ISTJ': ['ISTP', 'ESTP'],
        'ESTJ': ['ISTP', 'ESTP']
    }

    counselors_with_scores = [
        (counselor[0], counselor[1], counselor[2], counselor[3], counselor[4], counselor[5], 20 if counselor[2] in best_mbti_matches.get(child_mbti, []) else 0)
        for counselor in counselors
    ]

    # 점수가 높은 순서대로 정렬
    sorted_counselors = sorted(counselors_with_scores, key=lambda x: x[6], reverse=True)
    return sorted_counselors







@app.route('/mbti_match', methods=['GET', 'POST'])
def counselor_match():
    # session에서 child_id를 안전하게 문자열로 변환
    child_id = str(session.get('child_id')).strip()

    if not child_id:
        return "Child ID is not set in session.", 400
    print("db 아이디 :" ,child_id)
    
    if child_id is None:
        return "Child ID is not set in session.", 400

    filter_value = request.form.get('filter') if request.method == 'POST' else '0'

    function_mapping = {
        '0': all_match,
        '1': consulting_match,
        '2': get_best_match_counselors,
        '3': scope_match,
        '4': priority_match
    }

    filter_function = function_mapping.get(filter_value)
    if filter_function is None:
        return "Invalid filter option.", 400

    result = filter_function(child_id)

    if not result:
        return "No counselor found with the given filter.", 404

    reviews = [
        {   'co_id':row[0],
            'co_name': row[1],
            'avg_consulting_scope': int(row[4]) if row[4] is not None else 0,
            'co_mbti': row[2],
            'co_consulting': row[3],
            'consulting_priorities': row[5] if row[5] is not None else '없음'
        }
        for row in result
]

    

    if request.method == 'POST':
        reviews_html = ""
        for review in reviews:
            reviews_html += f"""
            <a class="list" href="/mbti_match_detail/{ review['co_id']}">
                <img src="/static/images/profile.png" alt="Profile" class="profile-pic" />
                <div class="list-text">
                    <span class="list-name">{review['co_name']}</span>
                    <span class="list-rating"><i class="bx bxs-star"></i>{review['avg_consulting_scope']}</span>
                    <p>{review['co_mbti']}</p>
                </div>
                <div class="list-details">
                    <p>{review['co_consulting']}</p>
                    <p>{review['consulting_priorities']}</p>
                </div>
            </a>
            """
        return jsonify({
            'html': reviews_html,
            'count': len(reviews)
        })
    else:
        return render_template('user/mbti_match.html', reviews=reviews)

def consulting_match(child_id):
    if child_id is None:
        return []

    query = """
            SELECT 
                c.co_id, 
                c.co_name, 
                c.co_mbti, 
                c.co_consulting, 
                AVG(r.consulting_scope) AS avg_consulting_scope,
                GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority) AS consulting_priorities
            FROM 
                COUNSELOR.counselor_list AS c
            JOIN 
                CHILD_INFO.child_info_list AS ci 
                ON c.co_consulting LIKE CONCAT('%%', ci.survey_consulting, '%%')
            LEFT JOIN 
                REVIEW.review_list AS r 
                ON c.co_id = r.co_id
            WHERE 
                ci.child_id = %s
            GROUP BY
                c.co_id, c.co_name, c.co_mbti, c.co_consulting;
    """
    print(f"Executing consulting_match query with child_id: {child_id}")  # Debugging line
    print("주요분야 쿼리:", query)  # 쿼리 출력
    return counselordb.execute(query, (child_id,))


def scope_match(child_id):
    if child_id is None:
        return []

    query = f"""
        SELECT 
            c.co_id,
            c.co_name,  
            c.co_mbti,
            c.co_consulting, 
            AVG(r.consulting_scope) AS avg_consulting_scope,
            GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority) AS consulting_priorities
        FROM 
            REVIEW.review_list AS r
        JOIN 
            COUNSELOR.counselor_list AS c ON c.co_id = r.co_id
        GROUP BY 
            c.co_id, 
            c.co_name, 
            c.co_consulting, 
            c.co_mbti
        ORDER BY 
            avg_consulting_scope DESC;
    """
    print(f"Executing scope_match query: {query}")  # Debugging line
    return counselordb.execute(query)

def all_match(child_id):
    if child_id is None:
        return []

    query = """

        -- 첫 번째 쿼리: 상담사 정보와 리뷰 정보
        WITH CounselorReview AS (
            SELECT 
                c.co_id,  
                c.co_name, 
                c.co_mbti, 
                c.co_consulting, 
                AVG(CASE WHEN r.consulting_scope IS NULL THEN 0 ELSE r.consulting_scope END) AS avg_consulting_scope,
                GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority) AS consulting_priorities,
                CASE WHEN AVG(CASE WHEN r.consulting_scope IS NULL THEN 0 ELSE r.consulting_scope END) > 4.0 THEN 10 ELSE 0 END AS totalscore
            FROM 
                COUNSELOR.counselor_list AS c
            LEFT JOIN 
                REVIEW.review_list AS r ON c.co_id = r.co_id 
            GROUP BY  
                c.co_id, c.co_name, c.co_mbti, c.co_consulting
        )

        -- 두 번째 쿼리: 전체 상담사 정보와 특정 어린이의 상담 우선순위 정보와 조인 및 점수 계산
        SELECT 
            cr.co_id, 
            cr.co_name, 
            cr.co_mbti, 
            cr.co_consulting, 
            cr.avg_consulting_scope AS consulting_scope, 
            cr.consulting_priorities AS consulting_priority
        FROM 
            CounselorReview AS cr
        JOIN 
            CHILD_INFO.child_info_list AS ci 
        ON ci.child_id = %s
        ORDER BY 
            cr.totalscore +
                CASE 
                    WHEN ci.survey_consulting IS NOT NULL AND cr.co_consulting LIKE CONCAT('%%', ci.survey_consulting, '%%') THEN 40 
                    ELSE 0 
                END +
                CASE 
                    WHEN (
                        (CASE WHEN ci.survey_priority_1 IS NOT NULL AND FIND_IN_SET(ci.survey_priority_1, cr.consulting_priorities) THEN 5 ELSE 0 END) +
                        (CASE WHEN ci.survey_priority_2 IS NOT NULL AND FIND_IN_SET(ci.survey_priority_2, cr.consulting_priorities) THEN 4 ELSE 0 END) +
                        (CASE WHEN ci.survey_priority_3 IS NOT NULL AND FIND_IN_SET(ci.survey_priority_3, cr.consulting_priorities) THEN 3 ELSE 0 END) +
                        (CASE WHEN ci.survey_priority_4 IS NOT NULL AND FIND_IN_SET(ci.survey_priority_4, cr.consulting_priorities) THEN 2 ELSE 0 END)
                    ) > 10 THEN 30
                    ELSE 10
                END +
                CASE
                    WHEN ci.child_mbti = 'INFP' AND cr.co_mbti IN ('ENFJ', 'ENTJ') THEN 20
                    WHEN ci.child_mbti = 'ENFP' AND cr.co_mbti IN ('ENFJ', 'ENTJ') THEN 20
                    WHEN ci.child_mbti = 'INFJ' AND cr.co_mbti IN ('ENFP', 'ENTP') THEN 20
                    WHEN ci.child_mbti = 'ENFJ' AND cr.co_mbti IN ('ENFP', 'ENTJ', 'ENTP') THEN 20
                    WHEN ci.child_mbti = 'INTJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ENTJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'INTP' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ENTP' AND cr.co_mbti IN ('ESTP') THEN 20
                    WHEN ci.child_mbti = 'ISFP' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ESFP' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ISTP' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ESTP' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ISFJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ESFJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ISTJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    WHEN ci.child_mbti = 'ESTJ' AND cr.co_mbti IN ('ISTP', 'ESTP') THEN 20
                    ELSE 0
                END DESC;
 
    """
    print(f"Executing all_match query with child_id: {child_id}")
    return counselordb.execute(query, (child_id,))


def priority_match(child_id):
    if child_id is None:
        return []

    query = """
            SELECT
                co.co_id,
                co.co_name,
                co.co_mbti, -- 상담사의 MBTI
                co.co_consulting, -- 상담사의 상담 유형
                AVG(r.consulting_scope) AS avg_consulting_scope,
                GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority) AS consulting_priorities,
                SUM(CASE
                    WHEN r.consulting_priority = c.survey_priority_1 THEN 5
                    WHEN r.consulting_priority = c.survey_priority_2 THEN 4
                    WHEN r.consulting_priority = c.survey_priority_3 THEN 3
                    WHEN r.consulting_priority = c.survey_priority_4 THEN 2
                    ELSE 0
                END) AS total_rating
            FROM
                CHILD_INFO.child_info_list c
            LEFT JOIN
                COUNSELOR.counselor_list co ON 1=1
            LEFT JOIN
                REVIEW.review_list r ON co.co_id = r.co_id AND (
                    r.consulting_priority = c.survey_priority_1 OR
                    r.consulting_priority = c.survey_priority_2 OR
                    r.consulting_priority = c.survey_priority_3 OR
                    r.consulting_priority = c.survey_priority_4
                )
            WHERE
                c.child_id = %s
            GROUP BY
                c.child_id, c.child_name, co.co_id, co.co_name, co.co_mbti, co.co_consulting
            ORDER BY
                total_rating DESC;
    """
    print(f"Executing priority_match query with child_id: {child_id}")
    return child_infodb.execute(query, (child_id,))

@app.route('/mbti_match_detail/<counselor_id>', endpoint='mbti_match_detail')
def mbti_match_detail_html(counselor_id):
    child_id = session.get('child_id')
    counselor_name_query = """
        SELECT co_name
        FROM COUNSELOR.counselor_list
        WHERE co_id = %s
    """
    counselor_name_data = counselordb.execute(counselor_name_query, (counselor_id,))
    counselor_name = counselor_name_data[0][0] if counselor_name_data else 'Unknown'

    query = """
        SELECT day_of_week, start_time, end_time
        FROM COUNSELOR_SCHEDULE.schedule_list
        WHERE co_id = %s
    """
    schedule_data = schedule_listdb.execute(query, (counselor_id,))

    days = ['월', '화', '수', '목', '금']
    times = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']

    schedule = {day: {time: False for time in times} for day in days}

    for day in days:
        schedule[day]['12:00'] = True

    for row in schedule_data:
        day_of_week, start_time, end_time = row
        
        if isinstance(start_time, timedelta):
            start_time = (datetime.min + start_time).time()
        if isinstance(end_time, timedelta):
            end_time = (datetime.min + end_time).time()

        start_idx = times.index(start_time.strftime('%H:%M'))

        end_idx = times.index(end_time.strftime('%H:%M')) if end_time.strftime('%H:%M') in times else len(times)

        for idx in range(start_idx, end_idx):
            schedule[day_of_week][times[idx]] = True

    return render_template('user/mbti_match_detail.html', counselor_name=counselor_name, schedule=schedule, days=days, times=times, counselor_id=counselor_id)

@app.route('/submit_selection/<int:counselor_id>', methods=['POST'])
def submit_selection(counselor_id):
    try:
        data = request.json
        selected_times = data.get('selectedTimes', [])
        child_id = session.get('child_id')

        current_counselor_query = """
            SELECT co_id FROM CHILD_INFO.child_info_list
            WHERE child_id = %s
        """
        current_counselor_data = child_infodb.execute(current_counselor_query, (child_id,))
        current_counselor_id = current_counselor_data[0][0] if current_counselor_data else None

        if current_counselor_id and current_counselor_id != counselor_id:
            return jsonify({
                'success': False,
                'require_confirmation': True,
                'message': '기존 상담사가 존재합니다. 상담사를 변경하시겠습니까?'
            }), 200

        merged_times = merge_times(selected_times, counselor_id)

        print("Merged Times:")
        for time_slot in merged_times:
            print(time_slot)

        consultation_code = random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=5))
        
        for time_slot in merged_times:
            day_of_week = convert_day_of_week(time_slot['day_of_week'])
            start_time = time_slot['start_time']
            end_time = time_slot['end_time']

            insert_query = f"""
                INSERT INTO COUNSELOR_SCHEDULE.schedule_list (co_id, child_id, day_of_week, start_time, end_time, consultation_code)
                VALUES ({counselor_id}, '{child_id}', '{day_of_week}', '{start_time}', '{end_time}', '{consultation_code}')
            """
            try:
                schedule_listdb.insert(insert_query)
            except Exception as e:
                print(f"Failed to execute query: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500

        update_query = f"""
            UPDATE CHILD_INFO.child_info_list
            SET co_id = {counselor_id}
            WHERE child_id = '{child_id}'
        """
        try:
            child_infodb.update(update_query)
        except Exception as e:
            print(f"Failed to execute update query: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

        return jsonify({'success': True}), 200

    except Exception as e:
        logging.error(f"Error in submit_selection: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/confirm_change_selection/<int:counselor_id>', methods=['POST'])
def confirm_change_selection(counselor_id):
    try:
        data = request.json
        selected_times = data.get('selectedTimes', [])
        child_id = session.get('child_id')

        delete_query = f"""
            DELETE FROM COUNSELOR_SCHEDULE.schedule_list
            WHERE child_id = '{child_id}'
        """
        print(f"Executing delete query: {delete_query}")
        try:
            schedule_listdb.delete(delete_query)
        except Exception as e:
            print(f"Failed to execute delete query: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

        merged_times = merge_times(selected_times, counselor_id)

        print("Merged Times:")
        for time_slot in merged_times:
            print(time_slot)

        consultation_code = random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=5))
        
        for time_slot in merged_times:
            day_of_week = convert_day_of_week(time_slot['day_of_week'])
            start_time = time_slot['start_time']
            end_time = time_slot['end_time']

            insert_query = f"""
                INSERT INTO COUNSELOR_SCHEDULE.schedule_list (co_id, child_id, day_of_week, start_time, end_time, consultation_code)
                VALUES ({counselor_id}, '{child_id}', '{day_of_week}', '{start_time}', '{end_time}', '{consultation_code}')
            """
            try:
                schedule_listdb.insert(insert_query)
            except Exception as e:
                print(f"Failed to execute query: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
            
        update_query = f"""
            UPDATE CHILD_INFO.child_info_list
            SET co_id = {counselor_id}
            WHERE child_id = '{child_id}'
        """
        try:
            child_infodb.update(update_query)
        except Exception as e:
            print(f"Failed to execute update query: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

        return jsonify({'success': True}), 200

    except Exception as e:
        logging.error(f"Error in confirm_change_selection: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/change_selection/<int:counselor_id>', methods=['POST'])
def change_selection(counselor_id):
    try:
        data = request.json
        selected_times = data.get('selectedTimes', [])
        child_id = session.get('child_id')

        current_counselor_query = """
            SELECT co_id FROM CHILD_INFO.child_info_list
            WHERE child_id = %s
        """
        current_counselor_data = child_infodb.execute(current_counselor_query, (child_id,))
        current_counselor_id = current_counselor_data[0][0] if current_counselor_data else None

        if current_counselor_id and current_counselor_id != counselor_id:
            return jsonify({
                'success': False,
                'message': '상담사를 다시 확인해 주세요.'
            }), 200

        delete_query = f"""
            DELETE FROM COUNSELOR_SCHEDULE.schedule_list
            WHERE child_id = '{child_id}'
        """
        try:
            schedule_listdb.delete(delete_query)
        except Exception as e:
            print(f"Failed to execute delete query: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

        merged_times = merge_times(selected_times, counselor_id)

        consultation_code = random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=5))

        for time_slot in merged_times:
            day_of_week = convert_day_of_week(time_slot['day_of_week'])
            start_time = time_slot['start_time']
            end_time = time_slot['end_time']

            insert_query = f"""
                INSERT INTO COUNSELOR_SCHEDULE.schedule_list (co_id, child_id, day_of_week, start_time, end_time, consultation_code)
                VALUES ({counselor_id}, '{child_id}', '{day_of_week}', '{start_time}', '{end_time}', '{consultation_code}')
            """
            try:
                schedule_listdb.insert(insert_query)
            except Exception as e:
                print(f"Failed to execute query: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500

        return jsonify({'success': True}), 200

    except Exception as e:
        logging.error(f"Error in change_selection: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def convert_day_of_week(day):
    day_map = {
        "월요일": "월",
        "화요일": "화",
        "수요일": "수",
        "목요일": "목",
        "금요일": "금",
        "토요일": "토",
        "일요일": "일"
    }
    return day_map.get(day, day)

def merge_times(selected_times, co_id):
    merged_times = []
    times_by_day = {}

    for time_slot in selected_times:
        day_of_week = time_slot['day_of_week']
        start_time = datetime.strptime(time_slot['start_time'], '%H:%M').time()
        end_time = datetime.strptime(time_slot['end_time'], '%H:%M').time()

        if day_of_week not in times_by_day:
            times_by_day[day_of_week] = []

        times_by_day[day_of_week].append((start_time, end_time))

    for day, times in times_by_day.items():
        times.sort()

        current_start = times[0][0]
        current_end = times[0][1]

        for start_time, end_time in times[1:]:
            if start_time <= current_end:
                current_end = max(current_end, end_time)
            else:
                merged_times.append({
                    'co_id': co_id,
                    'day_of_week': day,
                    'start_time': current_start.strftime('%H:%M'),
                    'end_time': current_end.strftime('%H:%M')
                })
                current_start = start_time
                current_end = end_time

        merged_times.append({
            'co_id': co_id,
            'day_of_week': day,
            'start_time': current_start.strftime('%H:%M'),
            'end_time': current_end.strftime('%H:%M')
        })

    return merged_times

@app.route('/get_counselor_schedule')
def get_counselor_schedule():
    counselor_id = request.args.get('counselorId')
    if not counselor_id:
        return "상담사 ID가 제공되지 않았습니다.", 400

    try:
        query = f"""
            SELECT day_of_week, start_time, end_time
            FROM schedule_list
            WHERE co_id = '{counselor_id}'
        """
        schedule = schedule_listdb.execute(query)

        # datetime.timedelta를 문자열로 변환
        reserved_timeslots = []
        for day, start, end in schedule:
            start_time = (datetime.min + start).time()
            end_time = (datetime.min + end).time()
            reserved_timeslots.append((day, start_time.strftime('%H:%M'), end_time.strftime('%H:%M')))

        # 예약 가능한 시간대를 계산
        available_timeslots = [
            timeslot for timeslot in AVAILABLE_TIMESLOTS if timeslot not in reserved_timeslots
        ]
    except Exception as e:
        app.logger.error(f"Error fetching schedule: {e}")
        return "서버 오류가 발생했습니다.", 500

    return render_template('user/get_counselor_schedule.html', counselor_id=counselor_id, reserved_timeslots=reserved_timeslots, available_timeslots=available_timeslots)


@app.route('/reserve_timeslot', methods=['POST'])
def reserve_timeslot():
    data = request.get_json()
    app.logger.info(f"Received data: {data}")  # 수신된 데이터 로그 출력

    # 세션에서 child_id 가져오기
    child_id = session.get('child_id')
    counselor_id = data.get('counselorId')
    day = data.get('day')
    start = data.get('start')
    end = data.get('end')

    # 모든 필드가 존재하는지 확인
    if not all([counselor_id, child_id, day, start, end]):
        app.logger.error("Missing required fields")
        return jsonify({"error": "모든 필드를 입력해주세요."}), 400

    try:
        # start와 end 시간을 datetime으로 변환
        start_time = datetime.strptime(start, '%H:%M').time()
        end_time = datetime.strptime(end, '%H:%M').time()

        # 현재 배정된 상담사 확인
        check_co_query = """
            SELECT co_id FROM child_info_list
            WHERE child_id = %s
        """
        child_infodb_cursor = child_infodb.get_cursor()
        child_infodb_cursor.execute(check_co_query, (child_id,))
        current_co_id_result = child_infodb_cursor.fetchone()

        if current_co_id_result:
            current_co_id = current_co_id_result[0]
            if current_co_id and current_co_id != counselor_id:
                app.logger.error("Child already assigned to a different counselor")
                child_infodb_cursor.close()  # 커서 닫기
                return jsonify({"error": "이미 다른 상담사에게 배정된 아동입니다."}), 400
        else:
            # co_id가 없으면 삽입
            insert_co_query = """
                INSERT INTO child_info_list (child_id, co_id)
                VALUES (%s, %s)
            """
            child_infodb_cursor.execute(insert_co_query, (child_id, counselor_id))

        # 중복 예약 확인
        check_query = """
            SELECT COUNT(*) FROM schedule_list
            WHERE co_id = %s AND child_id = %s AND day_of_week = %s
        """
        cursor = schedule_listdb.get_cursor()
        cursor.execute(check_query, (counselor_id, child_id, day))
        count = cursor.fetchone()[0]

        if count > 0:
            app.logger.error("Duplicate entry found")
            cursor.close()  # 커서 닫기
            return jsonify({"error": "동일한 요일에는 예약을 할 수 없습니다."}), 400

        # 상담 코드를 포함하여 새로운 일정 항목을 데이터베이스에 삽입하는 SQL 쿼리
        consultation_code = random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=5))

        insert_query = """
            INSERT INTO schedule_list (co_id, child_id, day_of_week, start_time, end_time, consultation_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (counselor_id, child_id, day, start_time, end_time, consultation_code))
        
        schedule_listdb.conn.commit()  # 트랜잭션 커밋
        child_infodb.conn.commit()  # 트랜잭션 커밋
        cursor.close()  # 커서 닫기
        child_infodb_cursor.close()  # 커서 닫기

        return jsonify({"success": True, "consultation_code": consultation_code}), 200
    except Exception as e:
        app.logger.error(f"Error reserving timeslot: {e}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500



@app.route('/mbti_result') 
def mbti_result_html():
    return render_template('user/mbti_result.html')

@app.route('/save_mbti_result', methods=['POST'])
def save_mbti_result():
    try:
        child_id = session.get('child_id')
        if not child_id:
            return jsonify({"error": "로그인을 해주세요."}), 401

        data = request.get_json()  # JSON 데이터 가져오기
        child_mbti = data.get('result') 

        if not child_mbti:
            return jsonify({"error": "MBTI 결과가 제공되지 않았습니다."}), 400

        insert_query = f"""
            UPDATE CHILD_INFO.child_info_list 
            SET child_mbti = '{child_mbti}' 
            WHERE child_id = '{child_id}';
        """
        child_infodb.insert(insert_query)
        return jsonify({"message": "저장 완료"}), 200

    except Exception as e:
        error_message = '오류가 발생했습니다.'
        print(f"Error Type: {type(e)}")
        print(f"Error Details: {e}")
        return jsonify({"error": "오류가 발생하여 MBTI 저장에 실패했습니다."}), 500


@app.route('/mbti_test') 
def mbti_test_html():
    return render_template('user/mbti_test.html')

@app.route('/user_counseling') 
def user_counseling_html():
    return render_template('user/user_counseling.html')

@app.route('/chat') 
def chat_html():
    
    return render_template('user/chat.html')

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    child_id = data.get('child_id')

    # 세션에서 해당 child_id에 대한 정보가 있는지 확인하고, 있으면 삭제
    if child_id in session:
        session.pop(child_id, None)
        return jsonify({'success': True, 'message': f'Logout successful for child_id {child_id}'})
    else:
        return jsonify({'success': False, 'message': 'No session found for this child_id'}), 404
    
@app.route('/cologout', methods=['POST'])
def cologout():
    try:
        data = request.get_json()
        counselor_id = data.get('counselor_ID')
        print(counselor_id)

       
        if counselor_id in session:
            print(f"세션에서 발견된 상담사 ID: {counselor_id}, 로그아웃 처리 진행")
            session.pop(counselor_id, None)
            
            print(f"{counselor_id} 로그아웃 성공")
            # 세션 정보 확인 (디버깅 용)
            print("현재 세션 상태:", dict(session))
        else:
            print(f"세션에서 상담사 ID: {counselor_id}를 찾을 수 없음.")

        return jsonify({'message': 'Logout successful'})

    except Exception as e:
        print(f"로그아웃 처리 중 오류 발생: {e}")
        return jsonify({'error': 'Logout failed', 'message': str(e)}), 500
    
@app.route('/roomcode', methods=['POST'])
def handle_room_code():
    # 요청 본문에서 roomCode를 추출합니다.
    data = request.get_json()
    room_code = data['roomCode']
    
    
    print('Received Room Code:', room_code)
    
    # 데이터베이스에서 consultation_code가 roomCode와 일치하는 co_id를 조회합니다.
    sql_query = """
    SELECT co_id
    FROM schedule_list
    WHERE consultation_code = %s;
    """
    results = schedule_listdb.query(sql_query, (room_code,))

    # 결과 반환
    if results:
        co_id = results[0][0]  # 첫 번째 행의 첫 번째 열 값만 추출
        print(co_id)
        return jsonify({'co_id': co_id})
    else:
        return jsonify({'message': 'No matching counselor found for the given room code.'})
    
@app.route('/review', methods=['POST'])
def handle_review_submission():
    # 요청 본문에서 데이터를 추출합니다.
    data = request.get_json()
    rating = data['rating']
    reviewText = data['reviewText'].replace("'", "\\'")  # SQL 인젝션 방지를 위한 간단한 처리
    reviewDate = data['reviewDate']
    childID = data['childID']
    counselorID = data['counselorID']
    tags = data['tags'].replace("'", "\\'")  # SQL 인젝션 방지를 위한 간단한 처리

    # 데이터를 콘솔에 출력합니다.
    print('Received rating:', rating)
    print('Received review text:', reviewText)
    print('Received review date:', reviewDate)
    print('Received child ID:', childID)
    print('Received counselorID:', counselorID)
    print('Received tags:', tags)

    # 상담사 이름을 조회합니다.
    sql_query = f"SELECT co_name FROM COUNSELOR.counselor_list WHERE co_id = '{counselorID}';"
    results = counselordb.query(sql_query)
    if results:
        counselor_name = results[0][0]
        print(counselor_name)

        # 상담 정보를 데이터베이스에 저장합니다.
        insert_consulting_sql = f"""
        INSERT INTO consulting_list (child_id, co_id, consulting_day)
        VALUES ('{childID}', '{counselorID}', '{reviewDate}');
        """
        try:
            consulting_listdb.insert(insert_consulting_sql)
            # 리뷰 정보를 데이터베이스에 저장합니다.
            insert_review_sql = f"""
            INSERT INTO review_list (co_id, co_name, child_id, consulting_day, consulting_priority, consulting_scope, consulting_etc)
            VALUES ('{counselorID}', '{counselor_name}', '{childID}', '{reviewDate}', '{tags}', '{rating}', '{reviewText}');
            """
            try:
                review_listdb.insert(insert_review_sql)
                return jsonify({'message': 'Review submitted successfully'})
            except Exception as e:
                print(e)
                return jsonify({'message': 'Failed to submit review due to an error in saving the review information'})
        except Exception as e:
            print(e)
            return jsonify({'message': 'Failed to submit review due to an error in saving the consulting information'})
    else:
        return jsonify({'message': 'Counselor not found'})

@app.route('/counselor/<co_id>')
def counselor_detail(co_id):
    query = f"""
            SELECT 
                r.co_name,
                r.consulting_priority,
                r.consulting_scope,
                r.consulting_etc,
                r.child_id,
                c.co_mbti,
                c.co_consulting,
                ch.child_name  
            FROM 
                REVIEW.review_list r
            JOIN 
                COUNSELOR.counselor_list c ON r.co_id = c.co_id
            JOIN 
                CHILD.child_list ch ON r.child_id = ch.child_id  
            WHERE 
                r.co_id = {co_id};
    """
    result = review_listdb.execute(query)
    print(result)

    if not result:
        return "No counselor found with the given ID.", 404

    # 첫 번째 행에서 상담사 이름, MBTI, 상담 분야 추출
    counselor_name = result[0][0]
    #counselor_priority = result[0][1]
    #counselor_scope = result[0][2]
    #counselor_etc = result[0][3]
    child_id = result[0][4]
    counselor_mbti = result[0][5]
    counselor_consulting = result[0][6]
    #child_name = result[0][7]
    
    # 리뷰 데이터를 리스트로 저장
    reviews = [
        {
            'child_name': row[7],
            'counselor_scope': int(row[2]),
            'counselor_consulting': row[1],
            'counselor_etc': row[3]
        }
        for row in result
    ]
    # 별점 개수 계산
    star_counts = Counter([review['counselor_scope'] for review in reviews])
    total_reviews = len(reviews)
    
    # 별점 평균 계산
    average_rating = sum(review['counselor_scope'] for review in reviews) / total_reviews if total_reviews > 0 else 0
    

    # 상담사 정보를 템플릿에 전달
    return render_template('user/user_review_ detail.html',
                           counselor_name=counselor_name,
                           counselor_mbti=counselor_mbti,
                           counselor_consulting=counselor_consulting,
                           reviews=reviews,
                           star_counts=star_counts,
                           total_reviews=total_reviews,
                           average_rating=average_rating)




    

@app.route('/reviewcheck', methods=['POST'])
def review_check():
    # 클라이언트로부터 전송된 데이터를 받기
    consultation_areas = request.form.getlist('consultationAreas[]')
    keywords = request.form.getlist('keywords[]')
    mbti = request.form.getlist('mbti[]')
    search_query = request.form.get('searchQuery', None)  # 상담사 이름 검색값 받기 (기본값은 None)

    # 데이터 로깅
    print("Received consultation areas:", consultation_areas)
    print("Received keywords:", keywords)
    print("Received MBTI types:", mbti)
    print("Received search query:", search_query)

    # SQL 쿼리를 안전하게 생성하기 위해 매개변수를 문자열로 결합
    consultation_area_str = "'" + "', '".join(consultation_areas) + "'"
    mbti_str = "'" + "', '".join(mbti) + "'"
    keyword_str = "'" + "', '".join(keywords) + "'"

    # 기본 SQL 쿼리 구성
    query = f"""
            SELECT 
                c.co_name,
                GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority SEPARATOR ', ') AS consulting_priorities,
                AVG(r.consulting_scope) AS avg_consulting_scope,
                c.co_mbti,
                c.co_consulting,
                c.co_id
            FROM
                REVIEW.review_list r
            JOIN
                COUNSELOR.counselor_list c ON c.co_name = r.co_name
            WHERE
                c.co_consulting IN ({consultation_area_str}) OR
                c.co_mbti IN ({mbti_str}) OR
                r.consulting_priority IN({keyword_str})
    """

    # searchQuery가 제공된 경우 쿼리에 추가
    if search_query:
        query += f" OR c.co_name LIKE '%{search_query}%'"

    query += " GROUP BY c.co_id ORDER BY c.co_name;"

    # DB 쿼리 실행
    result = review_listdb.execute(query)
    print(result)
    result_html = ""
    for row in result:
        co_name, consulting_priorities, avg_consulting_scope, co_mbti, co_consulting, co_id = row
        rating = round(avg_consulting_scope)
        result_html += f"""
        <a class="list" href="counselor/{co_id}">
              <img src="/static/images/profile.png" alt="Profile" class="profile-pic" />
              <div class="list-text">
                <span class="list-name">{co_name}</span>
                <span class="list-rating"><i class="bx bxs-star"></i>{rating}</span>
                <p>{co_mbti}</p>
              </div>
              <div class="list-details">
                <p>{co_consulting}</p>
                <p>{consulting_priorities}</p>
              </div>
            </a>
        """
    return result_html



@app.route('/reviewall', methods=['POST'])
def review_all():
    # 데이터베이스에서 정보를 가져오는 SQL 쿼리 실행
    query = """
        SELECT 
            c.co_name,
            GROUP_CONCAT(DISTINCT r.consulting_priority ORDER BY r.consulting_priority SEPARATOR ', ') AS consulting_priorities,
            AVG(r.consulting_scope) AS avg_consulting_scope,
            c.co_mbti,
            c.co_consulting,
            c.co_id
        FROM
            REVIEW.review_list r
        JOIN
            COUNSELOR.counselor_list c ON c.co_name = r.co_name
        GROUP BY 
            c.co_id
        ORDER BY 
            c.co_name;
    """
    
    result=review_listdb.execute(query)
    print(result)
    
    result_html = ""
    for row in result:
        co_name, consulting_priorities, avg_consulting_scope, co_mbti, co_consulting, co_id = row
        rating = round(avg_consulting_scope)
        
        result_html += f"""
        <a class="list" href="counselor/{co_id}">
              <img src="/static/images/profile.png" alt="Profile" class="profile-pic" />
              <div class="list-text">
                <span class="list-name">{co_name}</span>
                <span class="list-rating"><i class="bx bxs-star"></i>{rating}</span>
                <p>{co_mbti}</p>
              </div>
              <div class="list-details">
                <p>{co_consulting}</p>
                <p>{consulting_priorities}</p>
              </div>
            </a>
        """
    return result_html
        


# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


clients = {}

@socketio.on('register_child')
def handle_register_child(data):
    child_name = data.get('childName')
    clients[child_name] = request.sid
    print(f"Registered child: {child_name}, SID: {request.sid}")

@socketio.on('start_counseling')
def handle_start_counseling(data):
    child_name = data.get('childName')
    child_code = data.get('code')
    print("아동 이름:", child_name)
    print("아동 코드:",child_code)
    
    # 특정 아동에게만 메시지를 전송합니다.
    if child_name in clients:
        recipient_sid = clients[child_name]
        socketio.emit('counseling_started', {'message': '상담이 시작되었습니다.','code': child_code}, room=recipient_sid)
    else:
        print("해당하는 아동이 없습니다.")

    # 상담이 시작되었다는 메시지를 모든 연결된 클라이언트에게 전송합니다.
    #socketio.emit('counseling_started', {'message': '상담이 시작되었습니다.'})
    

users = {}
rooms = {}

@socketio.on('connect')
def handle_connect():
    print("Client connected: " + request.sid)
    users[request.sid] = None

@socketio.on('disconnect')
def handle_disconnect():
    room = users.pop(request.sid, None)
    if room is not None:
        print(f"Client disconnected: {request.sid} from : {room}")
        leave_room(room)
        emit("userDisconnected", request.sid, room=room)
        print_log("onDisconnect", request.sid, room)

@socketio.on('joinRoom')
def handle_join_room(room):
    if room not in rooms:
        join_room(room)
        emit("created", room)
        users[request.sid] = room
        rooms[room] = request.sid
    participants = list(socketio.server.manager.get_participants('/', room))
    if len(participants) == 1:
        join_room(room)
        emit("joined", room)
        users[request.sid] = room
        emit("setCaller", rooms[room])
    else:
        emit("full", room)
    print_log("onReady", request.sid, room)


@socketio.on('ready')
def handle_ready(room):
    emit("ready", room, room=room)
    print_log("onReady", request.sid, room)

@socketio.on('candidate')
def handle_candidate(payload):
    room = payload["room"]
    emit("candidate", payload, room=room)
    print_log("onCandidate", request.sid, room)

@socketio.on('offer')
def handle_offer(payload):
    room = payload["room"]
    sdp = payload["sdp"]
    emit("offer", sdp, room=room)
    print_log("onOffer", request.sid, room)

@socketio.on('answer')
def handle_answer(payload):
    room = payload["room"]
    sdp = payload["sdp"]
    emit("answer", sdp, room=room)
    print_log("onAnswer", request.sid, room)

def handle_leave_room(room):
    leave_room(room)
    # 사용자를 rooms 딕셔너리에서 제거합니다.
    if request.sid in users:
        del users[request.sid]

    # 방에 더 이상 참가자가 없는지 확인합니다.
    participants = list(socketio.server.manager.get_participants('/', room))
    if len(participants) == 0:
        # 방을 rooms 딕셔너리에서 삭제합니다.
        if room in rooms:
            del rooms[room]

    print_log("onLeaveRoom", request.sid, room)

def print_log(header, client_id, room):
    if room is None:
        return
    participants_list = list(socketio.server.manager.get_participants('/', room))
    size = len(participants_list)

    logging.info("#ConncetedClients - {} => room: {}, count: {}".format(header, room, size))



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=False)