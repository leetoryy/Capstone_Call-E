from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def render_tempaltes():
    template_names =[
        'counselor/join.html',
        'counselor/home.html',
        'counselor/child_list.html',
        'user/home.html',
        'user/mbti_home.html',
        'user/mbti_match.html',
        'user/mbti_result.html',
        'user/mbti_test.html'
    ]
    return render_template('counselor/join.html',template_names=template_names)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)