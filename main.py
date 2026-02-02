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
    safe_title = title.replace("'", "")
    safe_text = text.replace("'", "")
    cmd = f"osascript -e 'display notification \"{safe_text}\" with title \"{safe_title}\" sound name \"Glass\"'"
    os.system(cmd)

def try_play_video(driver):
    """
    여러 방법으로 재생 버튼 클릭을 시도하고 성공 여부를 반환하는 함수
    """
    # 1. 메인 프레임에서 시도
    try:
        # 재생 중인지 확인 (vjs-playing 클래스 존재 여부)
        playing_elements = driver.find_elements(By.CSS_SELECTOR, ".vjs-playing")
        if playing_elements:
            print("   ✅ 이미 재생 중입니다.")
            return True

        play_btn = driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
        if play_btn and play_btn[0].is_displayed():
            play_btn[0].click()
            print("   🖱️ 메인 프레임 재생 버튼 클릭")
            return True
    except:
        pass

    # 2. iframe 내부 탐색
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for idx, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)
            # iframe 내부에서 재생 중인지 확인
            if driver.find_elements(By.CSS_SELECTOR, ".vjs-playing"):
                print(f"   ✅ iframe[{idx}] 내부에서 이미 재생 중입니다.")
                return True
            
            play_btn = driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
            if play_btn and play_btn[0].is_displayed():
                play_btn[0].click()
                print(f"   🖱️ iframe[{idx}] 내부 재생 버튼 클릭")
                return True
            
            # 포스터 클릭 시도
            poster = driver.find_elements(By.CSS_SELECTOR, ".vjs-poster")
            if poster and poster[0].is_displayed():
                poster[0].click()
                print(f"   🖱️ iframe[{idx}] 내부 포스터 클릭")
                return True
            
            driver.switch_to.default_content() # 다음 iframe을 위해 복귀
        except:
            driver.switch_to.default_content()
            continue
            
    return False

def main():
    print("브라우저를 실행합니다 (스텔스 모드 적용)...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        print("lectures.json 데이터를 불러오는 중...")
        with open('lectures.json', 'r', encoding='utf-8') as f:
            lectures = json.load(f)

        todo_list = [l for l in lectures if not l.get('isCompleted', True)]
        total_todos = len(todo_list)
        print(f"총 {len(lectures)}개의 강의 중 {total_todos}개의 들을 강의가 있습니다.")

        driver.get("https://lms.kmooc.kr/login/index.php")
        print("브라우저에서 로그인을 완료해주세요.")
        input("로그인이 완료되면 엔터 키를 누르세요...")
        
        for idx, lecture in enumerate(todo_list, 1):
            title = lecture['title'].replace('\n', ' ')
            url = lecture['url']
            total_seconds = lecture['totalSeconds']
            
            print(f"\n[{idx}/{total_todos}] 진행 중: {title}")
            driver.get(url)
            
            # 재생 성공할 때까지 반복 시도 (최대 5회)
            play_started = False
            for attempt in range(1, 6):
                print(f"   🔍 재생 시도 중... ({attempt}/5)")
                time.sleep(random.randint(5, 8)) # 로딩 대기
                if try_play_video(driver):
                    play_started = True
                    break
                else:
                    print("   ⚠️ 재생 버튼을 찾지 못했습니다. 페이지를 다시 로드하거나 대기합니다.")
                    if attempt == 2: # 2번 실패 시 새로고침
                        driver.refresh()

            if not play_started:
                print("   ❌ 재생 시작을 확인하지 못했습니다. 수동 확인이 필요할 수 있습니다.")
                # 그래도 일단 대기는 수행 (사용자가 수동으로 눌렀을 가능성 대비)

            human_delay = random.randint(15, 60)
            wait_time = total_seconds + human_delay
            finish_time = time.strftime("%H:%M:%S", time.localtime(time.time() + wait_time))
            print(f"   ⏳ {wait_time}초 대기 시작 (종료 예정: {finish_time})")
            
            time.sleep(wait_time)
            
            print(f"   ✅ [{title}] 시청 완료.")
            notify_mac("강의 완료", f"{title} 시청 끝")

        print("\n모든 강의 수강이 완료되었습니다.")
        notify_mac("K-MOOC 봇", "모든 강의 수강이 완료되었습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        notify_mac("K-MOOC 봇 에러", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
