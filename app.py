from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, request,  redirect, url_for
from flask.json.provider import JSONProvider
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

import json
import sys


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
mongo = PyMongo(app)
api = Api(app)
jwt = JWTManager(app)

client = MongoClient('localhost', 27017)
db = client.dbjungle


#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################


#####
# 아래의 각각의 @app.route 은 RESTful API 하나에 대응됩니다.
# @app.route() 의 첫번째 인자는 API 경로,
# 생략 가능한 두번째 인자는 해당 경로에 적용 가능한 HTTP method 목록을 의미합니다.

# API #1: HTML 틀(template) 전달
#         틀 안에 데이터를 채워 넣어야 하는데 이는 아래 이어지는 /api/list 를 통해 이루어집니다.
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        if mongo.db.users.find_one({'username': username}):
            return '이미 존재하는 사용자입니다.'
        mongo.db.users.insert_one({'username': username, 'password': password_hash})
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(identity=username)
            return f'로그인 성공! 토큰: {access_token}'
        return '올바르지 않은 사용자 이름 또는 비밀번호입니다.'
    return render_template('login.html')

@app.route('/dashboard')
@jwt_required
def dashboard():
    current_user = get_jwt_identity()
    return f'로그인 성공! 대시보드에 오신 것을 환영합니다, {current_user}!'


if __name__ == '__main__':
    print(sys.executable)
    app.secret_key = 'your-secret-key'
    app.run('0.0.0.0', port=5000, debug=True)
