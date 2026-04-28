from flask import Blueprint, render_template, redirect, url_for
# db를 impoert한다.
from servers.flask.apps.app import db
# User 클래스를 import한다.
from servers.flask.apps.crud.models import User
from servers.flask.apps.crud.forms import UserForm
from flask_login import login_required

# Blueprint로 crud 앱을 생성한다.
crud = Blueprint('crud', __name__, template_folder='templates', static_folder='static')

# index 엔드포인트를 작성하고 index.html을 반환한다
@crud.route('/')
# 데코레이터를 추가한다.
@login_required
def index():
    return render_template('crud/index.html')

# 모등 엔드포인트에 @login_requiredf를 추가한다.
@crud.route('/sql')
@login_required
def sql():
    db.session.query(User).all()
    return '콘솔 로그를 확인해 주세요.'

@crud.route('/users')
@login_required
def users():
    """사용자의 일람을 취득한다."""
    users = User.query.all()
    return render_template("crud/index.html", users=users)

@crud.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    # UesrForm을 인스턴스화한다.
    form = UserForm()
    # 폼의 값을 검증한다.
    if form.validate_on_submit():
        # 사용자를 작성한다.
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        
        # 사용자를 추가하고 커밋한다.
        db.session.add(user)
        db.session.commit()

        # 사용자의 일람 화면으로 리다이렉트한다.
        return redirect(url_for('crud.users'))
    return render_template('crud/create.html', form=form)

# methods에 GET과 POST를 지정한다.
@crud.route("/users/<user_id>", methods=["GET","POST"])
@login_required
def edit_user(user_id):
    form = UserForm()

    # User 모델을 이용하여 사용자를 취득한다.
    user = User.query.filter_by(id=user_id).first()

    # form으로 제출된 경우는 사용자를 갱신하여 사용자의 일람 화면으로 리다이렉트한다.
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    # GET의 경우는 HTML을 반환한다.
    return render_template("crud/edit.html", user=user, form=form)

@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user=User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))

