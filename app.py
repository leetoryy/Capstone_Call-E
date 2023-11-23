from flask import Flask, render_template

app = Flask(__name__)

@app.route('/join.html') 
def join_html():
    return render_template('counselor/join.html')

@app.route('/counselor/home.html') 
def counselor_home_html():
    return render_template('counselor/home.html')

@app.route('/counselor/child_list.html') 
def child_list_html():
    return render_template('counselor/child_list.html')

@app.route('/user/home.html') 
def user_home_html():
    return render_template('user/home.html')

@app.route('/user/mbti_home.html') 
def mbti_home_html():
    return render_template('user/mbti_home.html')

@app.route('/user/mbti_match.html') 
def mbti_match_html():
    return render_template('user/mbti_match.html')

@app.route('/user/mbti_result.html') 
def mbti_result_html():
    return render_template('user/mbti_result.html')

@app.route('/user/mbti_test.html') 
def mbti_test_html():
    return render_template('user/mbti_test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=False)
