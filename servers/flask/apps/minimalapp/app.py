from flask import Flask,render_template, url_for,request, current_app,g, redirect,flash, session, make_response
from email_validator import validate_email, EmailNotValidError
import logging
import os
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message

app = Flask(__name__)
# SECRET_KEY룰 추가한다.
app.config['SECRET_KEY'] = 'your_secret_key'
# 로그 레벨을 설정한다.
app.logger.setLevel(logging.DEBUG)
app.logger.critical('fatal error')
app.logger.error('error')
app.logger.warning('warning')
app.logger.info('info')
app.logger.debug('debug')

# 리다이렉트를 중단하지 않도록 한다.
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# DebugToolbarExtension에 애플리케이션을 선정한다.
toolbar = DebugToolbarExtension(app)

# Mail 클래스의 config를 추가한다.
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# flask=mail 확장을 등록한다.
mail = Mail(app)

# 쿠키로부터 값을 취득하기
# key를 지정한다.
username = request.cookies.get('username')

# 쿠기로 값을 설정하기
response = make_response(render_template('contact.html'))
# KEY와 VALUE를 설정한다.
response.set_cookie('username', 'DOHA')

# 쿠키로부터 값을 삭제하기
# Key를 지정한다.
response.delete_cookie('username')

#세션에 값을 설정하기
session['username'] = 'DOHA'

# 세션으로부터 값을 취득하기
username = session['username']

# 세션으로부터 값을 삭제하기
session.pop('username', None)


@app.route('/')
def index():
    return 'Hello, flaskbook!'

# Rule에 변수 지정하기 
@app.route('/hello/<name>', methods=['GET','POST'], endpoint='hello-endpoint')
def hello(name):
    # Python 3.6부터 도입된 f-string을 사용하여 문자열 정의
    return f'Hello, {name}!'

# flsdk2부터는 @app.get('hello', @app.post('hello')라고 기술하는 것이 가능'
# @app.get('/hello')
# @app.post('/hello')
# @ def hello():
#     return 'Hello, world!'

# show_name 엔드포인트를 작성한다.
@app.route('/name/<name>')
def show_name(name):
    # 변수를 템플릿 엔진에게 건넨다.
    return render_template('index.html', name=name)

with app.test_request_context("/users?updated=true"):
    # true가 출력된다.
    print(request.args.get('updated'))
    # /
    print(url_for('index'))
    # /hello/world
    print(url_for('hello-endpoint', name='world'))
    # /name/doha?page=1
    print(url_for('show_name', name='doha', page=1))


@app.route('/contact')
def contact():
    # 응답 객체를 취득한다.
    response = make_response(render_template('contact.html'))

    # 쿠키를 설정한다.
    response.set_cookie('flaskbook_key', 'cookie_value')

    # 세션을 설정한다.
    session['username'] = 'DOHA'

    # 응답 오브젝트를 반환한다.
    return response

@app.route('/contact/complete', methods=['GET', 'POST'])
def contact_complete():
    if request.method == 'POST':
        #form 속성을 사용해서 폼의 값을 취득한다.
        username = request.form['username']
        email = request.form['email']
        description = request.form['description']

        # 입력 체크
        is_valid = True

        if not username:
            flash('사용자명을 입력해주세요.')
            is_valid = False

        if not email:
            flash('이메일 주소를 입력해주세요.')
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash('유효한 이메일 주소를 입력해주세요.')
            is_valid = False
        
        if not description:
            flash('문의 내용을 입력해주세요.')
            is_valid = False
        
        if not is_valid:
            return redirect(url_for('contact'))

        # 이메일을 보낸다
        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username, 
            description=description
            )

        # 문의 완료 엔드포인트로 리다이렉트한다.

        flash('문의가 성공적으로 접수되었습니다.')
        return redirect(url_for('contact_complete'))
    return render_template('contact_complete.html')

def send_email(to, subject, template, **kwargs):
    """ 메일을 송신하는 함수"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)