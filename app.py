import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的學術文獻庫", layout="wide")

# 1. 串接 Google Sheets (使用你的 ID)
SHEET_ID = "1Hby00zSDEaPPUPbKfpesu-MXX2rdv_JfK0axTDPBby0"
# 強制轉為 CSV 下載連結
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=60) 
def load_data():
    try:
        # 讀取資料並清掉標題的前後空格
        data = pd.read_csv(CSV_URL)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        return None

df = load_data()

# --- 主介面 ---
st.title("📚 文獻知識庫檢索系統")

if df is None or df.empty:
    st.error("❌ 無法讀取資料。請檢查：Google 表格左上角 [檔案] > [共用] > [發佈到網路] 是否已點擊「發佈」。")
    st.info("目前的 CSV 連結: " + CSV_URL)
else:
    # 2. 側邊欄搜尋
    st.sidebar.header("🔍 搜尋篩選")
    search_query = st.sidebar.text_input("輸入關鍵字 (自動搜尋所有欄位)")

    # 3. 過濾邏輯
    display_df = df.copy()
    if search_query:
        # 全文檢索邏輯
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    st.write(f"📊 共有 {len(df)} 筆文獻 | 搜尋到 {len(display_df)} 筆")

    # 4. 顯示資料
    if display_df.empty:
        st.warning("找不到符合的內容，請縮短關鍵字再試一次。")
    else:
        for _, row in display_df.iterrows():
            # 自動找尋最像的欄位內容
            def get_col(names):
                for n in names:
                    if n in row and pd.notna(row[n]): return str(row[n])
                return "（無資料）"

            # 抓取各個欄位
            title = get_col(['篇名', 'Title'])
            year = get_col(['年份', 'Year'])
            gold_sentence = get_col(['文獻金句/內容截錄', '文獻金句'])
            content = get_col(['CC全文', 'CC 全文'])
            abstract = get_col(['Abstract', '摘要'])
            variables = get_col(['研究變數(自變數、依變數、中介變數、調節變數、控制變數)', '研究變數'])
            tags = get_col(['分類標籤', '標籤'])
            citation = get_col(['citation', 'Citation'])

            with st.expander(f"📖 {title} ({year})", expanded=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("#### ✨ 文獻金句")
                    st.info(gold_sentence)
                    st.markdown("#### 📝 CC 全文 / 筆記")
                    st.write(content)
                    st.markdown("#### 📄 Abstract")
                    st.caption(abstract)
                with col2:
                    st.success(f"**🔬 研究變數：**\n{variables}")
                    st.warning(f"**🏷️ 標籤：** {tags}")
                    st.markdown(f"**📜 Citation:**\n`{citation}`")
            st.markdown("---")
