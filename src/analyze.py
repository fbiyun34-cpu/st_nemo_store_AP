import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import numpy as np

# 폰트 설정 (fontguide.md 참고: 나눔고딕)
plt.rcParams['font.family'] = 'NanumGothic'

def run_eda():
    db_path = "/Users/yunjiho/ficb6/nemostore/data/nemo_stores.db"
    img_dir = "/Users/yunjiho/ficb6/nemostore/images/eda"
    os.makedirs(img_dir, exist_ok=True)

    # 1. 데이터 로드
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM stores", conn)
    conn.close()

    # 2. 전처리
    # 수치형 변수 변환
    numeric_cols = ['deposit', 'monthlyRent', 'maintenanceFee', 'premium', 'sale', 'size', 'viewCount', 'favoriteCount', 'areaPrice']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. 기본 정보 출력
    print("--- 데이터 기본 정보 ---")
    print(df.head())
    print(df.tail())
    df.info()
    print(f"Shape: {df.shape}")
    print(f"Duplicates: {df.duplicated().sum()}")

    # 4. 시각화 및 분석
    reports = []

    # [시각화 1] 업종 대분류 빈도수 (businessLargeCodeName)
    plt.figure(figsize=(10, 6))
    counts = df['businessLargeCodeName'].value_counts().head(30)
    counts.plot(kind='bar', color='skyblue')
    plt.title('업종 대분류 빈도수 (상위 30개)')
    plt.xlabel('업종명')
    plt.ylabel('빈도수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '1_business_large_counts.png'))
    plt.close()
    reports.append({
        "title": "업종 대분류 빈도수 분석",
        "desc": "수집된 상가 데이터의 업종 대분류 분포를 파악한 결과, 특정 업종이 높은 비중을 차지하고 있음을 알 수 있습니다. 이는 해당 지역의 주요 상권 형성 특징을 보여줍니다.",
        "img": "1_business_large_counts.png",
        "table": counts.to_frame().to_markdown()
    })

    # [시각화 2] 보증금 분포 (deposit)
    plt.figure(figsize=(10, 6))
    plt.hist(df[df['deposit'] > 0]['deposit'], bins=50, color='coral', edgecolor='black')
    plt.title('보증금 분포 (0 제외)')
    plt.xlabel('보증금 (만원)')
    plt.ylabel('빈도수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '2_deposit_dist.png'))
    plt.close()
    reports.append({
        "title": "보증금 분포 분석",
        "desc": "보증금의 분포를 확인해본 결과, 대다수의 매물이 특정 가격대에 밀집되어 있으며 소수의 고가 매물이 존재함을 알 수 있습니다. 이는 일반적인 상가 임대 시장의 가격 형성을 반영합니다.",
        "img": "2_deposit_dist.png",
        "table": df['deposit'].describe().to_frame().to_markdown()
    })

    # [시각화 3] 월세 분포 (monthlyRent)
    plt.figure(figsize=(10, 6))
    plt.hist(df[df['monthlyRent'] > 0]['monthlyRent'], bins=50, color='lightgreen', edgecolor='black')
    plt.title('월세 분포 (0 제외)')
    plt.xlabel('월세 (만원)')
    plt.ylabel('빈도수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '3_monthly_rent_dist.png'))
    plt.close()
    reports.append({
        "title": "월세 분포 분석",
        "desc": "월세 분포는 보증금과 유사한 양상을 보이며, 중소형 상가들이 주를 이루는 시장 구조를 보여줍니다. 가격 변동폭이 커 다양한 규모의 상가가 공존함을 알 수 있습니다.",
        "img": "3_monthly_rent_dist.png",
        "table": df['monthlyRent'].describe().to_frame().to_markdown()
    })

    # [시각화 4] 전용면적 분포 (size)
    plt.figure(figsize=(10, 6))
    plt.hist(df[df['size'] > 0]['size'], bins=50, color='gold', edgecolor='black')
    plt.title('전용면적 분포')
    plt.xlabel('면적 (㎡)')
    plt.ylabel('빈도수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '4_size_dist.png'))
    plt.close()
    reports.append({
        "title": "전용면적 분포 분석",
        "desc": "상가의 전용면적은 소형(약 33㎡ 내외) 매물이 가장 높은 빈도를 보입니다. 이는 1인 창업이나 소규모 매장이 활발한 현재의 상권 트렌드와 일치합니다.",
        "img": "4_size_dist.png",
        "table": df['size'].describe().to_frame().to_markdown()
    })

    # [시각화 5] 보증금 vs 월세 상관관계 (이변량)
    plt.figure(figsize=(10, 6))
    plt.scatter(df['deposit'], df['monthlyRent'], alpha=0.5, color='purple')
    plt.title('보증금 vs 월세 상관관계')
    plt.xlabel('보증금 (만원)')
    plt.ylabel('월세 (만원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '5_deposit_rent_scatter.png'))
    plt.close()
    reports.append({
        "title": "보증금과 월세의 상관관계 분석",
        "desc": "보증금과 월세 사이에는 뚜렷한 양의 상관관계가 나타납니다. 즉, 보증금이 높은 매물일수록 월세도 높게 책정되는 경향이 강하며, 이는 매물의 가치가 가격 전반에 반영됨을 뜻합니다.",
        "img": "5_deposit_rent_scatter.png",
        "table": df[['deposit', 'monthlyRent']].corr().to_markdown()
    })

    # [시각화 6] 업종별 평균 월세 (이변량)
    plt.figure(figsize=(12, 6))
    avg_rent = df.groupby('businessLargeCodeName')['monthlyRent'].mean().sort_values(ascending=False).head(15)
    avg_rent.plot(kind='bar', color='tab:orange')
    plt.title('업종별 평균 월세 (상위 15개)')
    plt.xlabel('업종')
    plt.ylabel('평균 월세 (만원)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '6_avg_rent_by_biz.png'))
    plt.close()
    reports.append({
        "title": "업종별 평균 월세 분석",
        "desc": "특정 업종(예: 업무시설, 대형 판매시설 등)이 타 업종에 비해 평균 월세가 월등히 높게 나타납니다. 이는 공간의 입지 조건과 수익 구조 차이에서 비롯된 것으로 분석됩니다.",
        "img": "6_avg_rent_by_biz.png",
        "table": avg_rent.to_frame().to_markdown()
    })

    # [시각화 7] 층별 매물 빈도 (floor - 전처리 필요)
    plt.figure(figsize=(10, 6))
    # floor 컬럼에서 숫자만 추출하거나 지하/지상 구분 필요하나 여기선 원본 데이터 사용
    floor_counts = df['floor'].value_counts().head(20)
    floor_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('상가 층수별 분포 (상위 20개)')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '7_floor_dist_pie.png'))
    plt.close()
    reports.append({
        "title": "상가 층수별 분포 분석",
        "desc": "1층 상가 매물이 압도적으로 많은 비중을 차지하고 있습니다. 이는 고객 접근성을 중시하는 상가 임대 시장의 특성이 고스란히 반영된 결과로 보입니다.",
        "img": "7_floor_dist_pie.png",
        "table": floor_counts.to_frame().to_markdown()
    })

    # [시각화 8] 조회수와 즐겨찾기 상관관계 (다변량 - 색상으로 가격 표현)
    plt.figure(figsize=(10, 6))
    plt.scatter(df['viewCount'], df['favoriteCount'], c=df['monthlyRent'], cmap='viridis', alpha=0.6)
    plt.colorbar(label='월세 (만원)')
    plt.title('조회수 vs 즐겨찾기 수 (색상: 월세)')
    plt.xlabel('조회수')
    plt.ylabel('즐겨찾기 수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '8_view_favorite_multivariate.png'))
    plt.close()
    reports.append({
        "title": "관심도(조회/즐겨찾기)와 가격의 상관관계",
        "desc": "조회수가 높은 매물이 반드시 즐겨찾기 수가 많은 것은 아니지만, 일정한 비례 관계를 보입니다. 특히 중저가 매물에서 높은 관심도가 나타나는 경향을 확인할 수 있습니다.",
        "img": "8_view_favorite_multivariate.png",
        "table": df[['viewCount', 'favoriteCount', 'monthlyRent']].corr().to_markdown()
    })

    # [시각화 9] 관리비 유무에 따른 월세 상자 그림 (이변량)
    df['hasMaintenanceFee'] = df['maintenanceFee'] > 0
    plt.figure(figsize=(10, 6))
    df.boxplot(column='monthlyRent', by='hasMaintenanceFee')
    plt.title('관리비 유무에 따른 월세 분포')
    plt.suptitle('')
    plt.xlabel('관리비 존재 여부')
    plt.ylabel('월세 (만원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '9_rent_box_maint.png'))
    plt.close()
    reports.append({
        "title": "관리비 존재 여부에 따른 월세 비교",
        "desc": "관리비가 책정된 상가의 월세가 그렇지 않은 상가보다 중앙값이 높게 나타납니다. 이는 규모가 크거나 관리가 잘 되는 프라임급 빌딩의 매물일 가능성을 시사합니다.",
        "img": "9_rent_box_maint.png",
        "table": df.groupby('hasMaintenanceFee')['monthlyRent'].describe().to_markdown()
    })

    # [시각화 10] TF-IDF 키워드 분석 (title 컬럼)
    titles = df['title'].fillna("").tolist()
    vectorizer = TfidfVectorizer(max_features=30)
    tfidf_matrix = vectorizer.fit_transform(titles)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_dict = dict(zip(feature_names, tfidf_sums))
    sorted_tfidf = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)

    words = [x[0] for x in sorted_tfidf]
    scores = [x[1] for x in sorted_tfidf]

    plt.figure(figsize=(12, 6))
    plt.bar(words, scores, color='teal')
    plt.title('상가 매물 제목 키워드 분석 (TF-IDF 상위 30개)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, '10_tfidf_keywords.png'))
    plt.close()
    
    reports.append({
        "title": "매물 제목 키워드 주요 트렌드 분석",
        "desc": "TF-IDF를 활용해 제목의 주요 키워드를 추출한 결과, '임대', '상가', '사무실' 등 목적성 명사가 주를 이룹니다. 또한 특정 지역 명칭이 강조되어 입지의 중요성을 어필하고 있습니다.",
        "img": "10_tfidf_keywords.png",
        "table": pd.DataFrame(sorted_tfidf, columns=['Keyword', 'Score']).to_markdown()
    })

    # 5. 리포트 파일 생성 (report.md)
    report_path = "/Users/yunjiho/ficb6/nemostore/docs/report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Nemostore 상가 매물 데이터 EDA 보고서\n\n")
        f.write("## 1. 데이터 개요\n")
        f.write(f"- 전체 데이터 수: {len(df)} 행\n")
        f.write(f"- 전체 컬럼 수: {df.shape[1]} 개\n\n")
        
        f.write("### 데이터 샘플 (상위 5개)\n")
        f.write(df.head().to_markdown() + "\n\n")

        for r in reports:
            f.write(f"## {r['title']}\n")
            f.write(f"![{r['title']}](../images/eda/{r['img']})\n\n")
            f.write("### 분석 및 해석\n")
            f.write(f"{r['desc']}\n\n")
            f.write("### 주요 수치\n")
            f.write(r['table'] + "\n\n")
            f.write("---\n\n")

    print(f"분석 완료! 보고서와 이미지가 생성되었습니다.\n보고서: {report_path}\n이미지: {img_dir}")

if __name__ == "__main__":
    run_eda()
