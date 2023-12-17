import logging
from multiprocessing import connection
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from dbcl import DBconnector
import pymysql
import dbcl
import datetime


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'call-e'

# DB 연결 객체 생성
childdb = DBconnector('CHILD')
calledb = DBconnector('CALL_E')
counselordb = DBconnector('COUNSELOR')
child_infodb = DBconnector('CHILD_INFO') #아동mbti, 아동사전설문지 내용, 아동매칭상담사및상담날짜 포함
review_listdb =  DBconnector('REVIEW')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'child':
            child_ID = request.form.get('ch_id2')
            child_pw = request.form.get('ch_pw_2')
            
            try:
                if authenticate_child(child_ID, child_pw):
                    print("성공")
                    # Store the child_id in the session
                    session['child_id'] = child_ID
                    return jsonify({'user_type': 'child'})

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
                    print("성공")
                    print(counselor_name)
                    return jsonify({'user_type': 'counselor', 'counselor_name': counselor_name})
                    
                else:
                    print("실패")
                    return "아이디 또는 비밀번호가 일치하지 않습니다."

            except Exception as e:
                print(f"Error: {e}")
                return "로그인 중 오류가 발생했습니다."


@app.route('/join', methods=[ 'GET','POST'])
def join_html():
    error_message = None

    if request.method == 'POST':
        user_type = request.form.get('user_type')

        if user_type == 'child':
        
            # 아동 회원가입 처리
            childName = request.form.get('ch_name')
            childId = request.form.get('ch_id')
            childPassword = request.form.get('ch_pw')
            childPhoneNum = request.form.get('ch_ph')
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
            counselorPhone = request.form.get('co_phone')
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


@app.route('/counselor_home') 
def counselor_home_html():
    counselor_name = request.args.get('counselor_name', '')  # URL 파라미터로부터 counselor_name을 가져옴
    return render_template('counselor/counselor_home.html', counselor_name=counselor_name)

@app.route('/child_list') 
def child_list_html():
    return render_template('counselor/child_list.html')

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

@app.route('/user_home')
def user_home_html():
    return render_template('user/user_home.html')

@app.route('/mbti_home')
def mbti_home_html():
    return render_template('user/mbti_home.html')

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


def get_best_counselors():
    all_combined_scores = combine_scores()
    results = []

    for child_id, scores in all_combined_scores.items():
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        child_results = {"child_id": child_id, "top_counselors": []}

        for co_id, total_score in sorted_scores:
            # Skip counselors with a total score of 0
            if total_score <= 0:
                continue

            # Retrieve counselor information
            query = f"SELECT co_id, co_name, co_consulting FROM COUNSELOR.counselor_list WHERE co_id = {co_id};"
            result = child_infodb.execute(query)

            # Check if the result is not empty
            if result:
                co_info = result[0]  # Assuming result is a list of tuples, take the first tuple
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

                    # Check if this is the first counselor
                    is_first_counselor = i == 0 and j == 0

                    result_html += f"""
                    <div class="row d-flex justify-content-center">
                        <div class="col-lg-6 mt-4">
                            <div class="member d-flex align-items-start">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4>{co_name}</h4>
                                    <hr class="my-1">
                                    {f'<div class="badge text-dark position-absolute" style="top: 1rem; right: 1rem; font-size: 1rem">Best 추천!</div>' if is_first_counselor else ''}
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
                            <div class="member d-flex align-items-start">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4> {co_id},{co_name}</h4>
                                    <hr class="my-1">
                                    <div class="badge text-dark position-absolute" style="top: 1rem; right: 1rem; font-size: 1rem">
                                        Best 추천!
                                    </div>
                                    
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
                            <div class="member d-flex align-items-start">
                                <div class="teampic">
                                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                                </div>
                                <div class="member-info">
                                    <h4>{co_name}</h4>
                                    <hr class="my-1">
                                    <div class="badge text-dark position-absolute" style="top: 1rem; right: 1rem; font-size: 1rem">
                                        Best 추천!
                                    </div>
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


    elif option_value == '3' :
        try:
        # SQL 쿼리
            query = """
            SELECT co_id, AVG(consulting_scope) AS avg_consulting_scope
            FROM REVIEW.review_list
            GROUP BY co_id
            ORDER BY avg_consulting_scope DESC;
        """

        # 쿼리 실행
            result = review_listdb.execute(query)

        # 결과를 HTML로 가공
            result_html = ""
            for row in result:
                co_id, avg_consulting_scope = row
                star_rating = round(avg_consulting_scope)

                result_html += f"""
                <div class="row d-flex justify-content-center">
                    <div class="col-lg-6 mt-4">
                        <div class="member d-flex align-items-start">
                            <div class="teampic">
                                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                            </div>
                            <div class="member-info">
                                <h4>{co_id}</h4>
                                <hr class="my-1">
                                <div class="badge text-dark position-absolute" style="top: 1rem; right: 1rem; font-size: 1rem">
                                    Best 추천!
                                </div>
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

    elif option_value == '4':
        try:
        # SQL 쿼리
            query = """
            SELECT co_id, AVG(consulting_scope) AS avg_consulting_scope
            FROM REVIEW.review_list
            GROUP BY co_id
            ORDER BY avg_consulting_scope DESC;
        """

        # 쿼리 실행
            result = review_listdb.execute(query)

        # 결과를 HTML로 가공
            result_html = ""
            for row in result:
                co_id, avg_consulting_scope = row
                star_rating = round(avg_consulting_scope)

                result_html += f"""
                <div class="row d-flex justify-content-center">
                    <div class="col-lg-6 mt-4">
                        <div class="member d-flex align-items-start">
                            <div class="teampic">
                                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" class="img-fluid" alt="">
                            </div>
                            <div class="member-info">
                                <h4>{co_id}</h4>
                                <hr class="my-1">
                                <div class="badge text-dark position-absolute" style="top: 1rem; right: 1rem; font-size: 1rem">
                                    Best 추천!
                                </div>
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

@app.route('/mbti_result') 
def mbti_result_html():
    return render_template('user/mbti_result.html')

@app.route('/mbti_test') 
def mbti_test_html():
    return render_template('user/mbti_test.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)