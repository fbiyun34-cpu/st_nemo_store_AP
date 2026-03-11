## 1) HTTP 요청정보와 헤더
Request URL
https://www.nemoapp.kr/api/store/search-list?CompletedOnly=false&NELat=37.55005722739491&NELng=126.76411861233562&SWLat=37.44916345800868&SWLng=126.65449705706368&Zoom=15&SortBy=29&PageIndex=0
Request Method
GET
Status Code
200 OK
Remote Address
3.168.178.122:443
Referrer Policy
strict-origin-when-cross-origin

priority
u=1, i
referer
https://www.nemoapp.kr/store
sec-ch-ua
"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"macOS"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
user-agent
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
## 2) Payload 정보
CompletedOnly=false&NELat=37.55005722739491&NELng=126.76411861233562&SWLat=37.44916345800868&SWLng=126.65449705706368&Zoom=15&SortBy=29&PageIndex=0

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)
{
    "items": [
        {
            
## 4) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장하기