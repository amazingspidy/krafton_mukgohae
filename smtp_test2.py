import smtplib
from email.mime.text import MIMEText


# (*)보낼 메일의 내용과 제목
content = """
임시 내용
"""
title = '메일 제목'

msg = MIMEText(content)
msg['Subject'] = title

# (*)메일의 발신자 메일 주소, 수신자 메일 주소, 앱비밀번호(발신자) 
sender = 'churn82@gmail.com'
receiver = 'pclass.shin@gmail.com'
app_password = 'dvtj hbej joks nujz'


# 세션 생성
with smtplib.SMTP('smtp.gmail.com', 587) as s:
    # TLS 암호화
    s.starttls()

    # 로그인 인증과 메일 보내기
    s.login(sender, app_password)
    s.sendmail(sender, receiver, msg.as_string())