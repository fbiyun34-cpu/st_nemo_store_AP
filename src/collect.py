import requests
import pandas as pd
import os
import sqlite3
import time

def collect_nemo_data():
    url = "https://www.nemoapp.kr/api/store/search-list"
    base_params = {
        "CompletedOnly": "false",
        "NELat": "37.55005722739491",
        "NELng": "126.76411861233562",
        "SWLat": "37.44916345800868",
        "SWLng": "126.65449705706368",
        "Zoom": "15",
        "SortBy": "29"
    }

    headers = {
        "referer": "https://www.nemoapp.kr/store",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }

    db_path = "/Users/yunjiho/ficb6/nemostore/data/nemo_stores.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    page_index = 0
    total_count = 0
    
    print(f"실시간 DB 저장 수집 시작: {url}")
    
    # DB 연결 (수집 시작 전 테이블 초기화)
    conn = sqlite3.connect(db_path)
    
    while True:
        params = base_params.copy()
        params["PageIndex"] = str(page_index)
        
        print(f"페이지 {page_index} 요청 중...", end=" ", flush=True)
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                print("\n더 이상 수집할 데이터가 없습니다.")
                break

            # 추가 정보를 위해 각 아이템에 lat, lng가 있는지 확인 (보통 항목에 포함됨)
            # 네모 API의 경우 items 내에 latitude, longitude 또는 lat, lng 키가 있는지 확인
            processed_items = []
            for item in items:
                # API 응답 구조에 따라 키 이름 확인 필요 (일반적으로 latitude, longitude)
                processed_items.append(item)

            # 데이터프레임 변환 및 즉시 저장
            df = pd.DataFrame(processed_items)
            # 수집 시작 시(page_index=0)에는 기존 테이블을 교체(replace), 이후에는 추가(append)
            if_exists_mode = "replace" if page_index == 0 else "append"
            df.astype(str).to_sql("stores", conn, if_exists=if_exists_mode, index=False)
            
            total_count += len(items)
            print(f"-> {len(items)}개 저장 완료 (누적: {total_count}개)")
            
            page_index += 1
            time.sleep(1) # 서버 부하 방지
            
        except Exception as e:
            print(f"\n페이지 {page_index} 수집 중 오류 발생: {e}")
            break

    conn.close()
    print(f"\n최종 완료: 총 {total_count}개의 데이터가 {db_path} 에 저장되었습니다.")

if __name__ == "__main__":
    collect_nemo_data()
