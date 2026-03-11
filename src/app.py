import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# 페이지 설정
st.set_page_config(
    page_title="Nemo Store 매물 대시보드",
    page_icon="🏠",
    layout="wide"
)

# 컬럼명 한글 매핑
COLUMN_MAPPING = {
    'title': '매물명',
    'priceTypeName': '거래종류',
    'deposit': '보증금(만)',
    'monthlyRent': '월세(만)',
    'premium': '권리금(만)',
    'sale': '매매가(만)',
    'maintenanceFee': '관리비(만)',
    'size': '면적(㎡)',
    'floor': '층',
    'businessLargeCodeName': '업종분류',
    'nearSubwayStation': '주변역',
    'createdDateUtc': '등록일',
    'viewCount': '조회수',
    'favoriteCount': '관심수'
}

# 데이터 로드 및 전처리
@st.cache_data
def load_data(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM stores", conn)
    conn.close()
    
    # 수치형 데이터 변환
    numeric_cols = ['deposit', 'monthlyRent', 'premium', 'sale', 'maintenanceFee', 'floor', 'groundFloor', 'size', 'viewCount', 'favoriteCount', 'areaPrice']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 사진 URL 리스트 변환 (문자열 -> 리스트)
    import ast
    def parse_urls(url_str):
        try:
            return ast.literal_eval(url_str) if isinstance(url_str, str) else url_str
        except:
            return []
            
    df['smallPhotoUrls'] = df['smallPhotoUrls'].apply(parse_urls)
    df['originPhotoUrls'] = df['originPhotoUrls'].apply(parse_urls)
    
    return df

# 데이터 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "nemo_stores.db")

try:
    if not os.path.exists(DB_PATH):
        st.error(f"데이터베이스 파일을 찾을 수 없습니다. 경로를 확인해주세요: {DB_PATH}")
        st.info("`python src/collect.py`를 실행하여 데이터를 먼저 수집해야 합니다.")
        st.stop()
    
    file_size = os.path.getsize(DB_PATH)
    if file_size == 0:
        st.error(f"데이터베이스 파일이 비어 있습니다 (0 bytes): {DB_PATH}")
        st.stop()
        
    df = load_data(DB_PATH)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.write(f"**현재 DB 경로:** `{DB_PATH}`")
    st.write(f"**파일 크기:** {os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 'N/A'} bytes")
    st.info("팁: `python src/collect.py`를 다시 실행하여 DB 파일을 초기화해보세요. "
            "만약 GitHub 배포 중이라면 DB 파일이 LFS 포인터로 올라가지 않았는지 확인이 필요합니다.")
    st.stop()

# 메인 제목
st.title("🏠 Nemo Store 매물 통합 대시보드")
st.markdown("수집된 상가 매물 데이터를 기반으로 원하는 조건을 검색하고 분석할 수 있습니다.")

# 사이드바 필터
st.sidebar.header("🔍 검색 및 필터 옵션")

# 1. 아티클 제목 검색
search_keyword = st.sidebar.text_input("매물명/제목 키워드 검색", "")

# 2. 가격 필터
st.sidebar.subheader("💰 가격 조건 (단위: 만원)")

# 보증금 필터
max_deposit = int(df['deposit'].max())
deposit_range = st.sidebar.slider("보증금 범위", 0, max_deposit, (0, max_deposit), step=1000)

# 월세 필터
max_rent = int(df['monthlyRent'].max())
rent_range = st.sidebar.slider("월세 범위", 0, max_rent, (0, max_rent), step=50)

# 권리금 필터
max_premium = int(df['premium'].max())
premium_range = st.sidebar.slider("권리금 범위", 0, max_premium, (0, max_premium), step=100)

# 3. 기타 필터
st.sidebar.subheader("📐 건물 정보")

# 면적 필터
max_size = float(df['size'].max())
size_range = st.sidebar.slider("전용면적(㎡)", 0.0, max_size, (0.0, max_size))

# 층수 필터
floors = sorted(df['floor'].unique().tolist())
selected_floors = st.sidebar.multiselect("층 선택", floors, default=[f for f in floors if f != 0])

# 업종 필터
biz_types = sorted(df['businessLargeCodeName'].unique().tolist())
selected_biz = st.sidebar.multiselect("업종 대분류 선택", biz_types, default=biz_types)

# 데이터 필터링 적용
filtered_df = df[
    (df['title'].str.contains(search_keyword, case=False, na=False)) &
    (df['deposit'] >= deposit_range[0]) & (df['deposit'] <= deposit_range[1]) &
    (df['monthlyRent'] >= rent_range[0]) & (df['monthlyRent'] <= rent_range[1]) &
    (df['premium'] >= premium_range[0]) & (df['premium'] <= premium_range[1]) &
    (df['size'] >= size_range[0]) & (df['size'] <= size_range[1]) &
    (df['floor'].isin(selected_floors)) &
    (df['businessLargeCodeName'].isin(selected_biz))
].copy()

# 벤치마킹 계산 (지역/업종별 평균 대비)
if not filtered_df.empty:
    avg_rent_by_biz = df.groupby('businessLargeCodeName')['monthlyRent'].mean().to_dict()
    filtered_df['avg_biz_rent'] = filtered_df['businessLargeCodeName'].map(avg_rent_by_biz)
    filtered_df['rent_diff_pct'] = ((filtered_df['monthlyRent'] - filtered_df['avg_biz_rent']) / filtered_df['avg_biz_rent'] * 100).fillna(0)

# 결과 요약 표시
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("검색된 매물 수", len(filtered_df))
with col2:
    st.metric("평균 보증금", f"{int(filtered_df['deposit'].mean() if not filtered_df.empty else 0):,}만")
with col3:
    st.metric("평균 월세", f"{int(filtered_df['monthlyRent'].mean() if not filtered_df.empty else 0):,}만")
with col4:
    avg_diff = filtered_df['rent_diff_pct'].mean() if not filtered_df.empty else 0
    st.metric("평균 대비 월세율", f"{avg_diff:+.1f}%", delta_color="inverse")

st.divider()

# 레이아웃 구성
tab1, tab2, tab3 = st.tabs(["🖼️ 이미지 갤러리", "📊 시장 데이터 분석", "📋 상세 리스트"])

# 상세 정보 팝업 함수
@st.dialog("매물 상세 정보", width="large")
def show_details(item):
    d_col1, d_col2 = st.columns([1, 1])
    
    with d_col1:
        # 이미지 슬라이더 (Carousel 대용)
        photos = item['originPhotoUrls']
        if photos:
            st.image(photos[0], use_container_width=True, caption=f"대표 이미지 (총 {len(photos)}장)")
            if len(photos) > 1:
                st.write("---")
                # 작은 이미지들 표시
                cols = st.columns(4)
                for i, p_url in enumerate(photos[1:min(9, len(photos))]):
                    cols[i % 4].image(p_url, use_container_width=True)
        else:
            st.warning("이미지가 없습니다.")
            
    with d_col2:
        st.subheader(item['title'])
        st.write(f"**업종:** {item['businessLargeCodeName']} ({item['businessMiddleCodeName']})")
        st.write(f"**거래:** {item['priceTypeName']}")
        
        info_col1, info_col2 = st.columns(2)
        info_col1.write(f"**보증금:** {int(item['deposit']):,}만원")
        info_col1.write(f"**월세:** {int(item['monthlyRent']):,}만원")
        info_col1.write(f"**권리금:** {int(item['premium']):,}만원")
        
        info_col2.write(f"**면적:** {item['size']:.2f}㎡")
        info_col2.write(f"**층:** {item['floor']}층 / {int(item['groundFloor'])}층")
        info_col2.write(f"**관리비:** {int(item['maintenanceFee']):,}만원")
        
        st.info(f"📍 **위치 정보:** {item['nearSubwayStation']}")
        
        # 벤치마킹 지표 표시
        diff = item['rent_diff_pct']
        color = "red" if diff > 0 else "blue"
        st.markdown(f"💡 이 매물은 동일 업종 평균 월세 대비 <span style='color:{color}; font-weight:bold;'>{diff:+.1f}%</span> 수준입니다.", unsafe_allow_html=True)
        
        st.write("---")
        st.write(f"👀 조회수: {item['viewCount']} | ❤️ 관심: {item['favoriteCount']}")
        st.write(f"📅 등록일: {item['createdDateUtc']}")

with tab1:
    if not filtered_df.empty:
        # 갤러리 뷰 (4열 구성)
        num_cols = 4
        container = st.container()
        for i in range(0, len(filtered_df), num_cols):
            cols = container.columns(num_cols)
            for j in range(num_cols):
                idx = i + j
                if idx < len(filtered_df):
                    item = filtered_df.iloc[idx]
                    with cols[j]:
                        with st.container(border=True):
                            img_url = item['smallPhotoUrls'][0] if item['smallPhotoUrls'] else "https://via.placeholder.com/300x200?text=No+Image"
                            st.image(img_url, use_container_width=True)
                            st.markdown(f"**{item['title'][:12]}...**")
                            st.caption(f"{item['priceTypeName']} {int(item['deposit'])}/{int(item['monthlyRent'])}")
                            if st.button("상세보기", key=f"btn_{item['id']}_{idx}"):
                                show_details(item)
    else:
        st.info("검색 조건에 맞는 매물이 없습니다.")

with tab2:
    st.subheader("업종 및 입지 분석")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # 업종 대분류 빈도수
        biz_counts = filtered_df['businessLargeCodeName'].value_counts().reset_index()
        biz_counts.columns = ['업종명', '매물 수']
        if not biz_counts.empty:
            fig = px.bar(
                biz_counts,
                x='업종명', 
                y='매물 수',
                title="업종별 매물 분포",
                color='매물 수',
                color_continuous_scale='ViridIs'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
    with viz_col2:
        # 층별 평균 임대료 분석
        if not filtered_df.empty:
            floor_rent = filtered_df.groupby('floor')['monthlyRent'].mean().reset_index()
            fig = px.bar(
                floor_rent,
                x='floor',
                y='monthlyRent',
                labels={'floor': '층', 'monthlyRent': '평균 월세(만)'},
                title="층별 평균 월세 분석",
                color='monthlyRent',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    viz_col3, viz_col4 = st.columns(2)
    
    with viz_col3:
        # 층수별 매물 비중
        floor_counts = filtered_df['floor'].value_counts().sort_index()
        if not floor_counts.empty:
            fig = px.pie(
                values=floor_counts.values, 
                names=floor_counts.index,
                title="층수별 매물 비중",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with viz_col4:
        # 면적 대비 임대료 산점도
        if not filtered_df.empty:
            fig = px.scatter(
                filtered_df,
                x='size',
                y='monthlyRent',
                color='businessLargeCodeName',
                size='deposit',
                hover_data=['title'],
                title="면적 대비 월세 분포 (크기: 보증금)",
                labels={'size': '면적(㎡)', 'monthlyRent': '월세(만)'}
            )
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("검색된 매물 목록")
    if not filtered_df.empty:
        # 컬럼명 한글 변환 적용
        display_df = filtered_df[list(COLUMN_MAPPING.keys())].rename(columns=COLUMN_MAPPING)
        st.dataframe(
            display_df.sort_values(by='등록일', ascending=False),
            use_container_width=True,
            column_config={
                "등록일": st.column_config.DatetimeColumn("등록일", format="YYYY-MM-DD")
            }
        )
    else:
        st.info("검색 조건에 맞는 매물이 없습니다.")

st.sidebar.markdown("---")
st.sidebar.info("Nemo Store Data Analysis Project Tools")


st.sidebar.markdown("---")
st.sidebar.info("Nemo Store Data Analysis Project Tools")
