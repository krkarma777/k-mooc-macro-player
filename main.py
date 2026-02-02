import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def main():
    # 1. 초기 설정
    print("브라우저를 실행합니다...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # 필요 시 주석 해제

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 2. 데이터 로드
        print("lectures.json 데이터를 불러오는 중...")
        with open('lectures.json', 'r', encoding='utf-8') as f:
            lectures = json.load(f)

        # isCompleted: false인 항목만 필터링
        todo_list = [l for l in lectures if not l.get('isCompleted', True)]
        total_todos = len(todo_list)
        print(f"총 {len(lectures)}개의 강의 중 {total_todos}개의 들을 강의가 있습니다.")

        # 3. 로그인 대기
        print("로그인 페이지로 이동합니다.")
        driver.get("https://lms.kmooc.kr/login/index.php")
        
        print("브라우저에서 로그인을 완료해주세요.")
        input("로그인이 완료되면 엔터 키를 누르세요...")
        # time.sleep(60) # 혹은 60초 대기

        # 4. 강의 순회
        for idx, lecture in enumerate(todo_list, 1):
            title = lecture['title'].replace('\n', ' ')
            url = lecture['url']
            total_seconds = lecture['totalSeconds']
            wait_time = total_seconds + 10

            print(f"\n[{idx}/{total_todos}] 진행 중: {title}")
            print(f"이동 URL: {url}")
            
            driver.get(url)
            
            print("페이지 로딩 대기 (5초)...")
            time.sleep(5)
            
            print(f"영상 재생 대기: {wait_time}초 동안 대기합니다...")
            time.sleep(wait_time)
            
            print(f"[{title}] 수강 완료 처리 예상 시간 경과.")

        print("\n모든 강의 수강이 완료되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        print("브라우저를 종료합니다.")
        driver.quit()

if __name__ == "__main__":
    main()
