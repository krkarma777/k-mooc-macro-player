import json
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def notify_mac(title, text):
    """
    맥OS 알림 센터에 메시지를 띄우는 함수
    """
    # 쉘 명령어 실행을 위해 텍스트 내의 따옴표 이스케이프 처리
    safe_title = title.replace("'", "")
    safe_text = text.replace("'", "")
    cmd = f"osascript -e 'display notification \"{safe_text}\" with title \"{safe_title}\" sound name \"Glass\"'"
    os.system(cmd)

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
            
            # 1. 페이지 로딩 대기 (네트워크 상황 고려하여 랜덤)
            time.sleep(random.randint(3, 6))

            # 2. 재생 버튼 강제 클릭 시도
            try:
                # Video.js의 큰 재생 버튼이 클릭 가능할 때까지 최대 10초 대기 후 클릭
                play_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".vjs-big-play-button"))
                )
                play_btn.click()
                print("   🖱️ 재생 버튼 클릭 성공")
            except Exception:
                # 버튼을 못 찾았거나 이미 재생 중인 경우 (포스터 클릭 시도)
                try:
                    poster = driver.find_element(By.CSS_SELECTOR, ".vjs-poster")
                    poster.click()
                    print("   🖱️ 포스터 이미지 클릭 성공")
                except:
                    print("   ⚠️ 재생 버튼/포스터를 찾지 못했습니다. (이미 재생 중이거나 자동 재생됨)")

            # 3. 인간적인 시청 패턴 시뮬레이션:
            # 영상 길이 + (10초 ~ 60초 사이의 랜덤한 여유 시간)
            human_delay = random.randint(10, 60)
            wait_time = total_seconds + human_delay
            
            # 로그에 남는 시간이 너무 기계적이지 않게 표시
            finish_time = time.strftime("%H:%M:%S", time.localtime(time.time() + wait_time))
            print(f"   ⏳ {wait_time}초 대기 중... (예상 종료: {finish_time})")
            
            time.sleep(wait_time)
            
            completion_msg = f"[{title}] 수강 완료 처리 예상 시간 경과."
            print(completion_msg)
            # 강의 완료 알림
            notify_mac("강의 완료", f"{title} 시청 끝")

        final_msg = "모든 강의 수강이 완료되었습니다."
        print(f"\n{final_msg}")
        # 전체 완료 알림
        notify_mac("K-MOOC 봇", final_msg)

    except Exception as e:
        err_msg = f"오류 발생: {e}"
        print(f"❌ {err_msg}")
        notify_mac("K-MOOC 봇 에러", str(e))
    finally:
        print("브라우저를 종료합니다.")
        driver.quit()

if __name__ == "__main__":
    main()
