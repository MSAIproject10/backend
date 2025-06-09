import threading
import schedule
import time
from shared.services.collector import run_collect
from shared.services.updater import run_update

def start_scheduler(): # 작업 스케쥴러를 초기화하는 함수 
    def job():
        run_collect()

    # schedule.every().day.at("09:00").do(job)  # KST 기준이면 Azure는 UTC이므로 "00:00"으로 조정 가능
    schedule.every(5).minutes.do(job)
    
    def run_schedule_loop(): # 실행할 작업이 있는지 체크해서 실행(60초마다 반복)
        while True:
            schedule.run_pending()
            time.sleep(60)

    threading.Thread(target=run_schedule_loop, daemon=True).start()
