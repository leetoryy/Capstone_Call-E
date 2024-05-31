import base64
import logging
from multiprocessing import connection
import traceback
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from dbcl import DBconnector
import pymysql
import dbcl
from datetime import datetime, time, timedelta
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
#code_listdb = DBconnector('CONSULTING_CODE)
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

                childdb.execute(insert_query)
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

                counselordb.execute(insert_query)
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
        # 클라이언트로부터 전달된 아이디
        child_id = request.form.get('child_id')

        # 데이터베이스에서 아이디 중복 확인
        query = f"SELECT COUNT(*) FROM CHILD.child_list WHERE child_id = '{child_id}'"
        result = childdb.execute(query)

        # 디버깅: 쿼리와 결과 확인
        print(f"Query: {query}")
        print(f"Query result: {result}")

        # 결과가 없는 경우에 대한 예외 처리
        if result is None or not result:
            raise Exception(f"Query returned no result for child_id '{child_id}'. Full result: {result}")

        # 결과를 JSON 형식으로 반환
        is_duplicate = result[0][0] > 0
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

    # SQL 결과물을 출력
    print("SQL Query Results:")
    for row in results:
        print(row)

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

    # 데이터가 올바르게 처리되었는지 출력
    print("Processed Data:")
    print(data)

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

    print("SQL Query today:")
    for row in results:
        print(row)

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


    print("today Data:")
    print(today_data)

    return jsonify(today_data)



@app.route('/counselor_home')
def counselor_home_html():
    counselor_name = request.args.get('counselor_name', '')
    co_id = session.get('co_id', '')
    return render_template('counselor/counselor_home.html', counselor_name=counselor_name)



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
        # 세션에서 상담사 아이디 가져오기
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
    
@app.route('/counsel_write') 
def counsel_write_html():
    return render_template('counselor/counsel_write.html')

@app.route('/counsel_view') 
def counsel_view_html():
    return render_template('counselor/counsel_view.html')

@app.route('/counsel_schedule') 
def counsel_schedule_html():
    return render_template('counselor/counsel_schedule.html')

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

@app.route('/survey_pre_edit')
def survey_pre_edit_html():
    return render_template('user/survey_pre_edit.html')

@app.route('/user_home')
def user_home_html():
    return render_template('user/user_home.html')

@app.route('/mbti_home')
def mbti_home_html():
    return render_template('user/mbti_home.html')

@app.route('/user_review')
def user_reivew_html():
    return render_template('user/user_review.html')

@app.route('/user_review_detail') 
def user_review_detail_html():
    return render_template('user/user_review_detail.html')

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

#mbti 점수 부여 - 20점  
Best_mbti = {
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

def get_child_mbti():
    query = "SELECT child_id, child_mbti FROM CHILD_INFO.child_info_list"
    result = child_infodb.fetch_all(query)
    return result

def get_counselor_mbti():
    query = "SELECT co_id, co_name, co_mbti FROM COUNSELOR.counselor_list"
    result = counselordb.fetch_all(query)
    return result

def mbti_match():
    result_mbti = {}

    child_mbti_results = get_child_mbti()
    counselor_mbti_results = get_counselor_mbti()

    for child_id, child_mbti in child_mbti_results:
        result_mbti[child_id] = {} 

        for co_id, co_name, co_mbti in counselor_mbti_results:
            if child_mbti in Best_mbti and co_mbti in Best_mbti[child_mbti]:
                result_mbti[child_id][co_id] = 20
            else:
                result_mbti[child_id][co_id] = 0

    return result_mbti

def combine_scores():
    scores_for_all = calculate_scores_for_all()
    scores_avg_consulting_scope = calculate_avg_consulting_scope()
    total_ratings = calculate_total_rating()
    mbti_match_results = mbti_match()

    combined_scores = {}

    for child_id, child_scores in scores_for_all.items():
        combined_scores[child_id] = {}

        for co_id, score_all in child_scores.items():
            score_avg_consulting_scope = scores_avg_consulting_scope.get(co_id, 0)
            total_rating = total_ratings.get(child_id, {}).get(co_id, 0)
            mbti_score = mbti_match_results.get(child_id, {}).get(co_id, 0)

            combined_score = score_all + score_avg_consulting_scope + total_rating + mbti_score

            combined_scores[child_id][co_id] = combined_score

    return combined_scores



def get_best_counselors():
    all_combined_scores = combine_scores()
    results = []

    for child_id, scores in all_combined_scores.items():
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        child_results = {"child_id": child_id, "top_counselors": []}

        for co_id, total_score in sorted_scores:
            if total_score <= 0:
                continue

            query = f"SELECT co_id, co_name, co_consulting FROM COUNSELOR.counselor_list WHERE co_id = {co_id};"
            result = child_infodb.execute(query)
         
            if result:
                co_info = result[0] 
                co_name, co_consulting = co_info[1], co_info[2]
                counselor_info = {
                    "co_id": co_id,
                    "co_name": co_name,
                    "co_consulting": co_consulting,
                    "total_score": total_score,
                }
                child_results["top_counselors"].append(counselor_info)

        results.append(child_results)

    return results

@app.route('/mbti_match', methods=['GET','POST'])
def print_matching_counselors():
    # Get the child_id from the session
    logged_in_child_id = session.get('child_id')
    option_value = request.form.get('option')

    if option_value == '0':
        best_counselors_result = get_best_counselors()

        result_html = ""

        for i, child_result in enumerate(best_counselors_result):
            child_id = child_result["child_id"]
            top_counselors = child_result["top_counselors"]

            # Check if the current child_id matches the logged-in child_id
            if logged_in_child_id and child_id != logged_in_child_id:
                continue

            if top_counselors:
                for j, counselor_info in enumerate(top_counselors):
                    co_id = counselor_info["co_id"]
                    co_name = counselor_info["co_name"]
                    co_consulting = counselor_info["co_consulting"]
                    total_score = counselor_info["total_score"]

                    

                    result_html += f"""
                    <div class="row d-flex justify-content-center">
                        <div class="col-lg-6 mt-4">
                            <div class="member d-flex align-items-start" data-counselor-id="{co_id}">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4>{co_name}</h4>
                                    <hr class="my-1">
                                    
                                    <p>{co_consulting}</p>
                                    <p>Total Score: {total_score}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
            else:
                result_html += f"일치하는 상담사가 없습니다: {child_id}<br>"

        return result_html
        
    elif option_value == '1':
        child_survey_consulting = get_all_child_survey_consulting()
        counselor_survey_consulting = get_all_counselor_survey_consulting()

        result_html = ""

        for child_row in child_survey_consulting:
            child_id, child_consulting = child_row

            # Check if the current child_id matches the logged-in child_id
            if logged_in_child_id and child_id != logged_in_child_id:
                continue

            matching_counselors = [
                (co_id, co_consulting, co_name) for co_id, co_consulting, co_name in counselor_survey_consulting
                if all(survey_consulting in co_consulting.split(', ') for survey_consulting in child_consulting.split(', '))
            ]

            if matching_counselors:
                for co_id, co_consulting, co_name in matching_counselors:
                    result_html += f"""
                    <div class="row d-flex justify-content-center">
                        <div class="col-lg-6 mt-4">
                            <div class="member d-flex align-items-start" data-counselor-id="{co_id}">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4> {co_name}</h4>
                                    <hr class="my-1">
                                    
                                    
                                    <p>{co_consulting}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
            else:
                result_html += f"일치하는 상담사가 없습니다: {child_id}<br>"

        return result_html

    elif option_value == '2':
        try:
            # SQL 쿼리
            query = """
                SELECT
                    c.child_id,
                    c.child_name,
                    r.co_id,
                    r.co_name,
                    SUM(CASE
                        WHEN r.consulting_priority = c.survey_priority_1 THEN 5
                        WHEN r.consulting_priority = c.survey_priority_2 THEN 4
                        WHEN r.consulting_priority = c.survey_priority_3 THEN 3
                        WHEN r.consulting_priority = c.survey_priority_4 THEN 2
                        ELSE 0
                    END) AS total_rating
                FROM
                    CHILD_INFO.child_info_list c
                JOIN
                    REVIEW.review_list r ON c.survey_priority_1 = r.consulting_priority
                    OR c.survey_priority_2 = r.consulting_priority
                    OR c.survey_priority_3 = r.consulting_priority
                    OR c.survey_priority_4 = r.consulting_priority
                GROUP BY
                    c.child_id, c.child_name, r.co_id, r.co_name
                ORDER BY
                    total_rating DESC;
            """
            # 쿼리 문자열을 출력해봅니다.

            # 쿼리 실행
            result = child_infodb.execute(query)

            # 결과를 HTML로 가공
            result_html = ""
            for row in result:
                child_id, child_name, co_id, co_name, total_rating = row

                # Check if the current child_id matches the logged-in child_id
                if logged_in_child_id and child_id != logged_in_child_id:
                    continue

                result_html += f"""
                    <div class="row d-flex justify-content-center">
                        <div class="col-lg-6 mt-4">
                            <div class="member d-flex align-items-start" data-counselor-id="{co_id}">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4>{co_name}</h4>
                                    <hr class="my-1">
                                    
                                    <p>Total Score: {total_rating}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                """
            # HTML 결과를 클라이언트에게 전달
            return result_html

        except Exception as e:
            print(f"Error calculating total rating: {e}")
            return None

    # MBTI 궁합순 상담사 추천
    elif option_value == '3':
        try:
            query_child = """
            SELECT child_id, child_mbti FROM CHILD_INFO.child_info_list
            """
            query_counselor = """
            SELECT co_id, co_mbti, co_name FROM COUNSELOR.counselor_list
            """
            result_child = child_infodb.execute(query_child)
            result_counselor = counselordb.execute(query_counselor)
            
            result_html = ""
            # Compatibility 함수를 이용하여 Child_mbti와 co_mbti 값의 궁합 점수 확인
            comp_results = []
            for child_id, child_mbti in result_child:
                for co_id, co_mbti, co_name in result_counselor:
                    comp_result = Compatibility(child_mbti, co_mbti)
                    
                    if comp_result is not None:
                        comp_results.append((child_id, co_id, co_name, comp_result))
            
            sorted_counselor = sorted(comp_results, key=lambda x:x[3], reverse=True)

            for child_id, co_id, co_name, comp_result in sorted_counselor:
                        result_html += f"""
                            <div class="row d-flex justify-content-center">
                                <div class="col-lg-6 mt-4">
                                    <div class="member d-flex align-items-start" data-counselor-id="{co_id}">
                                        <div class="teampic">
                                            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                        </div>
                                        <div class="member-info">
                                            <h4>{co_name}</h4>
                                            <hr class="my-1">                                 
                                            <p>{'❤️' * comp_result}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """

            return result_html

        except Exception as e:
            print(f"평균 호환성 계산 중 오류 발생: {e}")
            return None

    elif option_value == '4':
        try:
        # SQL 쿼리
            query = """
            SELECT co_name, co_id, AVG(consulting_scope) AS avg_consulting_scope
            FROM REVIEW.review_list
            GROUP BY co_id, co_name
            ORDER BY avg_consulting_scope DESC;
        """

        # 쿼리 실행
            result = review_listdb.execute(query)

        # 결과를 HTML로 가공
            result_html = ""
            for row in result:
                co_name, co_id, avg_consulting_scope = row
                star_rating = round(avg_consulting_scope)

                result_html += f"""
                <div class="row d-flex justify-content-center">
                    <div class="col-lg-6 mt-4">
                        <div class="member d-flex align-items-start" data-counselor-id="{co_id}">
                            <div class="teampic">
                                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                            </div>
                            <div class="member-info">
                                <h4>{co_name}</h4>
                                <hr class="my-1">
                                
                                <p>{star_rating}</p>
                                <div class="review-flex">
                                    {'⭐' *  star_rating}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """

            return result_html

        except Exception as e:
            print(f"Error calculating average consulting scope: {e}")
            return None
    return render_template('user/mbti_match.html')

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

    # 세션에서 child_name 가져오기
    child_id = session.get('child_name')
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
        
        # CHILD_INFO.child_info_list 테이블에 co_id, consultation_day, consultation_time 업데이트
        update_query = """
            UPDATE child_info_list
            SET co_id = %s, consultation_day = %s, consultation_time = %s
            WHERE child_id = %s
        """
        child_infodb_cursor = child_infodb.get_cursor()
        consultation_day = day
        consultation_time = start_time.strftime('%H:%M')
        child_infodb_cursor.execute(update_query, (counselor_id, consultation_day, consultation_time, child_id))
        
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
    child_id = session.get('child_id')
    if child_id:
        try:
            data = request.get_json()  # JSON 데이터 가져오기
            child_mbti = data.get('result') 
            insert_query = f"""
                UPDATE CHILD_INFO.child_info_list 
                SET child_mbti = '{child_mbti}' 
                WHERE child_id = '{child_id}';
            """
            child_infodb.insert(insert_query)
            return "저장 완료"

        except Exception as e:
            error_message = '오류가 발생했습니다.'
            print(f"Error Type: {type(e)}")
            print(f"Error Details: {e.args}")
            return "오류가 발생하여 MBTI 저장에 실패했습니다."
    else:
        return "로그인을 해주세요."

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