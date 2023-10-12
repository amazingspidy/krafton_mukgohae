from flask import Flask, render_template, jsonify, request, session, redirect, url_for

# email 모듈
import smtplib
from email.mime.text import MIMEText

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
import hashlib
from pymongo import MongoClient

from bson import ObjectId

# JWT 토큰을 만들 때 필요한 비밀문자열


app = Flask(__name__)
app.secret_key = 'MUKGOHAE'


app = Flask(__name__)
app.secret_key = 'MUKGOHAE'
# MongoDB에 연결
client = MongoClient('localhost', 27017)

# 데이터베이스 생성
db = client.dbmukgohae


@app.route('/')
def home():
    user_email = session.get('email', None)
    result = list(db.order.find({}))
    return render_template('main.html', orders=result, user_email=user_email)

# read_orders()
@app.route('/list', methods=['GET'])
def read_orders():
    current_date = str(datetime.datetime.now().date()).replace('-','')
    current_time = str(datetime.datetime.now().strftime("%H%M"))
    current_datetime = current_date + current_time
    
    order_datetime = ''
    
    valid_orders = []

    result = list(db.order.find({}))

    for i in result:
        i['_id'] = str(i['_id'])

    for order in result:
        order_date = order['order_date'].replace('-','')
        order_time = order['order_time'].replace(':','')
        order_datetime = order_date + order_time
        if (int(order_datetime) > int(current_datetime)):
            valid_orders.append(order)
    
    return jsonify({'result': 'success', 'orders': valid_orders})

@app.route('/plus', methods=['POST'])
def plus_curmem_num():
     
     id_receive = request.form['order_id']     
     order = db.order.find_one({'_id': ObjectId(id_receive)})
     
     # 참여하기 누르기 전 ppl num now 가져오기
     ppl_num_now = int(order['ppl_num_now'])
 
     # 1 증가
     ppl_num_new = ppl_num_now + 1

     # 증가 값 디비에 업뎃
     result = db.order.update_one({'_id': ObjectId(id_receive)}, {
                                    '$set': {'ppl_num_now': ppl_num_new}})
     
     # send_email()에 넘길 인자 가져오기
     order_owner_email = order['user_email']
     ppl_num_aim = int(order['ppl_num_aim'])

     # 목표인원 달성 시 (현재인원 >= 목표인원) send_email() 호출로 이메일 보내기
     if (ppl_num_new >= ppl_num_aim):
        send_email(order_owner_email)

     if result.modified_count == 1:
         return jsonify({'result': 'success'})
     else:
         return jsonify({'result': 'failure'})

    
# 이메일 함수
def send_email(order_owner_email):
    
    # (*)보낼 메일의 내용과 제목
    content = """
    목표인원이 달성되었습니다
    """
    title = '목표인원이 달성되었습니다.'

    msg = MIMEText(content)
    msg['Subject'] = title

    # (*)메일의 발신자 메일 주소, 수신자 메일 주소, 앱비밀번호(발신자) 
    sender = 'churn82@gmail.com'
    receiver = order_owner_email
    app_password = 'dvtj hbej joks nujz'


    # 세션 생성
    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        # TLS 암호화
        s.starttls()

        # 로그인 인증과 메일 보내기
        s.login(sender, app_password)
        s.sendmail(sender, receiver, msg.as_string())
        
    

    
    


@app.route('/add_member', methods=['POST'])
def add_member():
     # 1. order 목록에서 find_one으로 id기반으로 영화 하나를 찾습니다.
     id_receive = request.form['order_id']
     user_email = session.get('email', None)
     order = db.order.find_one({'_id': ObjectId(id_receive)})

     new_member = order['member_names']
     
     #user_email추가
     new_member.append(user_email)
     # 
     result = db.order.update_one({'_id': ObjectId(id_receive)}, {
                                    '$set': {'member_names': new_member}})

     if result.modified_count == 1:
         return jsonify({'result': 'success'})
     else:
         return jsonify({'result': 'failure'})

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/write')
def write():
    user_email = session.get('email', None)
    return render_template('write.html', user_email=user_email)

@app.route('/order_detail')
def order_detail():
    user_email = session.get('email', None)
    result = list(db.order.find({}))
    return render_template('order_detail.html', orders=result, user_email=user_email)


@app.route('/member_search', methods=['GET'])
def member_search():
    user_email = session.get('email', None)
    result = db.order.find_one({'member_names': user_email}, {'_id':0})

    return jsonify({'result': 'success', 'orders': result})
    #return render_template('order_detail.html', user_email=user_email)


# 회원가입
@app.route('/api/signup', methods=['POST'])
def api_register():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # 이미 존재하는 아이디면 패스!
    result = db.user.find_one({'email': email_receive})
    if result is not None:
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 EMAIL입니다!'})
    else:
        db.user.insert_one({'email': email_receive, 'pw': pw_hash, 'nick': nickname_receive})
        return jsonify({'result': 'success'})





# 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # email, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'email': email_receive, 'pw': pw_hash})

    if result is not None:
        # 사용자가 인증되었을 때 세션 또는 쿠키를 설정
        session['email'] = email_receive
        return jsonify({'result': 'success', 'message': '로그인 성공'})
    else:
        return jsonify({'result': 'fail', 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

#로그아웃
@app.route('/logout')
def logout():
    session.pop('email', None)  # 세션에서 사용자 정보 삭제
    return redirect(url_for('login'))  # 로그인 페이지로 리디렉션


#인증
@app.route('/api/secure', methods=['GET'])
def secure_api():
    if 'email' in session:
        # 사용자가 로그인되어 있을 때만 접근 가능
        return jsonify({'result': 'success', 'message': '인증된 사용자입니다.'})    
    else:
        return jsonify({'result': 'fail', 'message': '인증이 필요합니다.'})


@app.route('/write', methods=['POST'])
def write_order():
    
    print('test',request.form)
    user_email = session.get('email', None)
    order_date = request.form['order_date']
    order_time = request.form['order_time']
    food_category = request.form['food_category']
    with_who = request.form['with_who']
    food_shop = request.form['food_shop']
    food_name = request.form['food_name']
    ppl_num_aim = request.form['ppl_num_aim']
    ppl_num_max = request.form['ppl_num_max']
    ppl_num_now = request.form['ppl_num_now']
    place = request.form['place']
    account_num = request.form['account_num']
    

    db.order.insert_one({'user_email':user_email,
                         'order_date': order_date,
                         'order_time': order_time,
                         'food_category': food_category,
                         'with_who': with_who,
                         'food_shop': food_shop,
                         'food_name': food_name,
                         'ppl_num_aim': ppl_num_aim,
                         'ppl_num_max': ppl_num_max,
                         'ppl_num_now': ppl_num_now,
                         'member_names' : [],
                         'place' : place,
                         'account_num' : account_num,
                         'replys': [],
                        })
    return jsonify({'result': 'success'})

#업데이트로 추후 수정 예정
# @app.route('/update_order', methods=['POST'])
# def write_order():
#     place = request.form['place']
#     accout_num = request.form['accout_num']
    

#     db.order.update_one({'_id': ObjectId(id_receive)},{'$set': {'place': place}})
#     db.order.update_one({'_id': ObjectId(id_receive)},{'$set': {'accout_num': accout_num}})

#     return jsonify({'result': 'success'})







if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)