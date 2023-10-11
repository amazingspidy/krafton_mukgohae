import schedule # 미설치 시 !pip install schedule
import time

def my_job():
    print("[test] test 프린트 문  입니다.")

schedule.every(10).seconds.do(my_job)

while True:
    schedule.run_pending()
    time.sleep(1)
