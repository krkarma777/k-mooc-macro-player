import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def main():
    # 1. 초기 설정 (탐지 회피 옵션 추가)
    print("브라우저를 실행합니다 (스텔스 모드 적용)...")
    chrome_options = Options()
    # 봇 탐지 방지: '자동화된 소프트웨어' 알림 제거 및 webdriver 플래그 숨김
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # chrome_options.add_argument("--headless") # 필요 시 주석 해제

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Navigator.webdriver = false로 설정 (추가적인 안전장치)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

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
        
        # 4. 강의 순회
        for idx, lecture in enumerate(todo_list, 1):
            title = lecture['title'].replace('\n', ' ')
            url = lecture['url']
            total_seconds = lecture['totalSeconds']
            
            print(f"\n[{idx}/{total_todos}] 진행 중: {title}")
            print(f"이동 URL: {url}")
            driver.get(url)
            
            # 로딩 대기 (네트워크 상황 고려하여 랜덤)
            load_delay = random.randint(5, 10)
            print(f"페이지 로딩 대기 ({load_delay}초)...")
            time.sleep(load_delay)
            
            # 인간적인 시청 패턴 시뮬레이션:
            # 영상 길이 + (10초 ~ 60초 사이의 랜덤한 여유 시간)
            human_delay = random.randint(10, 60)
            wait_time = total_seconds + human_delay
            
            # 로그에 남는 시간이 너무 기계적이지 않게 표시
            finish_time = time.strftime("%H:%M:%S", time.localtime(time.time() + wait_time))
            print(f"⏳ {wait_time}초 대기 중... (예상 종료: {finish_time})")
            
            time.sleep(wait_time)
            
            print(f"[{title}] 수강 완료 처리 예상 시간 경과.")

        print("\n모든 강의 수강이 완료되었습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        print("브라우저를 종료합니다.")
        driver.quit()

if __name__ == "__main__":
    main()
