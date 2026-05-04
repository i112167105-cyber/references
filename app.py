import streamlit as st
import pandas as pd

st.set_page_config(page_title="學術文獻深度檢索系統", layout="wide")

# 1. 資料串接
SHEET_ID = "1Hby00zSDEaPPUPbKfpesu-MXX2rdv_JfK0axTDPBby0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60) 
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        return data
    except Exception as e:
        st.error(f"表格讀取失敗，請確認 Google 表格是否已「發佈到網路」並設為 CSV 格式。")
        return pd.DataFrame()

df = load_data()

# 2. 側邊欄搜尋
st.sidebar.header("🔍 檢索中心")
search_query = st.sidebar.text_input("輸入關鍵字 (搜尋全文/金句/摘要/變數/標籤)")

# 3. 搜尋邏輯 (自動過濾掉不存在的空值)
display_df = df.copy()
if search_query and not display_df.empty:
    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    display_df = display_df[mask]

# 4. 主介面
st.title("📚 我的學術文獻知識庫")

if display_df.empty:
    st.info("目前沒有資料，或找不到符合條件的結果。請檢查 Google 表格內容。")
else:
    for _, row in display_df.iterrows():
        # 這裡使用安全抓取資料的方式，就算欄位名稱不完全一樣也不會壞掉
        title = row.get('篇名', '未命名文獻')
        year = row.get('年份', '')
        
        with st.expander(f"📖 {title} ({year})", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 【文獻金句】")
                st.info(row.get('文獻金句/內容截錄', '無資料'))
                st.markdown("#### 【CC 全文 / 筆記】")
                st.write(row.get('CC全文', '無資料'))
                st.markdown("#### 【Abstract / 摘要】")
                st.caption(row.get('Abstract', '無資料'))
            with col2:
                st.success(f"**研究變數：**\n{row.get('研究變數(自變數、依變數、中介變數、調節變數、控制變數)', '無')}")
                st.warning(f"**標籤：** {row.get('分類標籤', '無')}")
                st.markdown(f"**Citation:**\n`{row.get('citation', '無')}`")
        st.markdown("---") # 用 markdown 的橫線代替 br，更穩定
