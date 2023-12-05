import logging
from multiprocessing import connection
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from dbcl import DBconnector
import pymysql
import dbcl
import datetime


app = Flask(__name__, static_url_path='/static')

# DB 연결 객체 생성
userdb = DBconnector('USER')
calledb = DBconnector('CALL_E')
counselordb = DBconnector('COUNSELOR')
surveydb = DBconnector('SURVEY')


# HTML 렌더링을 위한 기본 경로
@app.route('/')
def index():
    return render_template('counselor/join.html')

def authenticate_child(child_ID, child_pw):
    query = f"SELECT COUNT(*) FROM USER.user_list WHERE user_id = '{child_ID}' AND user_password = '{child_pw}'"
    result = userdb.execute(query)
    return result and result[0][0] == 1

def authenticate_counselor(counselor_ID, counselor_pw):
    query = f"SELECT COUNT(*) FROM COUNSELOR.counselor_list WHERE co_id = '{counselor_ID}' AND co_password = '{counselor_pw}'"
    result = counselordb.execute(query)
    return result and result[0][0] == 1

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'child':
            child_ID = request.form.get('ch_id2')
            child_pw = request.form.get('ch_pw_2')
            
            try:
                if authenticate_child(child_ID, child_pw):
                    print("성공")
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
                if authenticate_counselor(counselor_ID, counselor_pw):
                    print("성공")
                    return jsonify({'user_type': 'counselor'})
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
            
            try:
                birth_date_string = f"{childBirthYear}{childBirthMonth.zfill(2)}{childBirthDay.zfill(2)}"
                birth_date_int = int(birth_date_string)

                insert_query = f"""
                    INSERT INTO USER.user_list (user_name, user_id, user_password, user_phone, user_email,
                                    user_birth, user_address)
                    VALUES ('{childName}', '{childId}', '{childPassword}', '{childPhoneNum}', '{childEmail}',
                            {birth_date_int}, '{childAddress}');
                """

                userdb.insert(insert_query)
                print(f"Query: {insert_query}")
                return jsonify({'user_type': 'child'})
                
                
                
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
        query = f"SELECT COUNT(*) FROM USER.user_list WHERE user_id = '{child_id}'"
        result = userdb.execute(query)

        # 디버깅: 쿼리와 결과 확인
        print(f"Query: {query}")
        print(f"Query result: {result}")

        # 결과가 없는 경우에 대한 예외 처리
        if result is None or not result:
            raise Exception(f"Query returned no result for user_id '{child_id}'. Full result: {result}")

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
    return render_template('counselor/counselor_home.html')

@app.route('/child_listl') 
def child_list_html():
    return render_template('counselor/child_list.html')

@app.route('/survey_pre')
def survey_pre_html():
    return render_template('user/survey_pre.html')

@app.route('/user_home')
def user_home_html():
    return render_template('user/user_home.html')

@app.route('/mbti_home')
def mbti_home_html():
    return render_template('user/mbti_home.html')

@app.route('/mbti_match') 
def mbti_match_html():
    return render_template('user/mbti_match.html')

@app.route('/mbti_result') 
def mbti_result_html():
    return render_template('user/mbti_result.html')

@app.route('/mbti_test') 
def mbti_test_html():
    return render_template('user/mbti_test.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)