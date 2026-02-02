(function () {
    const videoElements = document.querySelectorAll('li.activity.vod');

    const videoData = Array.from(videoElements).map(li => {
        const linkAnchor = li.querySelector('a');
        const title = linkAnchor.querySelector('.instancename')?.innerText.replace(' 동영상', '').trim();

        // 1. URL 추출 (onclick 내 viewer 주소 우선, 없으면 href)
        const onclick = linkAnchor.getAttribute('onclick') || "";
        const urlMatch = onclick.match(/'(https:\/\/lms\.kmooc\.kr\/mod\/vod\/viewer\.php\?id=\d+)'/);
        const url = urlMatch ? urlMatch[1] : linkAnchor.href;

        // 2. 재생 시간 추출 (01:10, 36:53 등)
        const playTime = li.querySelector('.text-playtime')?.innerText.trim() || "00:00";

        // 3. 초 단위 변환 (프로그램 로직용)
        const timeParts = playTime.split(':').map(Number);
        let seconds = 0;
        if (timeParts.length === 2) seconds = (timeParts[0] * 60) + timeParts[1];
        else if (timeParts.length === 3) seconds = (timeParts[0] * 3600) + (timeParts[1] * 60) + timeParts[2];

        // 4. 완료 여부
        const isCompleted = !!li.querySelector('img[src*="completion-auto-y"]');

        return { title, url, playTime, totalSeconds: seconds, isCompleted };
    });

    console.table(videoData);
    copy(JSON.stringify(videoData, null, 2));
    console.log("✅ 데이터가 클립보드에 JSON 형식으로 복사되었습니다.");
})();