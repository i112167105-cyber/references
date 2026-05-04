import streamlit as st
import pandas as pd

# 頁面配置
st.set_page_config(page_title="學術文獻深度檢索系統", layout="wide")

# --- 1. 資料串接 ---
# 將你的 Google Sheets 網址轉為自動匯出 CSV 格式
SHEET_ID = "1Hby00zSDEaPPUPbKfpesu-MXX2rdv_JfK0axTDPBby0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600) # 每 10 分鐘自動更新一次資料
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        return data
    except Exception as e:
        st.error(f"資料讀取失敗，請確認表格是否開啟「知道連結的人皆可查看」: {e}")
        return pd.DataFrame()

df = load_data()

# --- 2. 側邊欄：進階篩選功能 ---
st.sidebar.header("🔍 檢索與篩選")

# 全文檢索框
search_query = st.sidebar.text_input("輸入關鍵字 (搜尋全文/篇名/摘要/變數/標籤)", placeholder="例如：AI 倫理")

# 多選篩選器
if not df.empty:
    tag_options = df["分類標籤"].dropna().unique().tolist() if "分類標籤" in df.columns else []
    selected_tags = st.sidebar.multiselect("分類標籤篩選", tag_options)
    
    method_options = df["研究方法"].dropna().unique().tolist() if "研究方法" in df.columns else []
    selected_methods = st.sidebar.multiselect("研究方法篩選", method_options)

# --- 3. 搜尋過濾邏輯 ---
display_df = df.copy()

if search_query:
    # 建立搜尋遮罩，掃描所有欄位（忽略大小寫）
    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
    display_df = display_df[mask]

if selected_tags:
    display_df = display_df[display_df["分類標籤"].isin(selected_tags)]

if selected_methods:
    display_df = display_df[display_df["研究方法"].isin(selected_methods)]

# --- 4. 主介面顯示 ---
st.title("📚 我的學術文獻知識庫")
st.write(f"當前收錄文獻：{len(df)} 筆 | 搜尋結果：{len(display_df)} 筆")

if display_df.empty:
    st.warning("找不到符合條件的文獻，請嘗試減少篩選條件或重新搜尋。")
else:
    for _, row in display_df.iterrows():
        # 使用卡片式容器顯示
        with st.expander(f"📖 {row.get('篇名', '未命名篇名')} ({row.get('年份', 'N/A')})", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 【文獻金句 / 核心論點】")
                st.info(row.get("文獻金句/內容截錄", "尚無資料"))
                
                st.markdown("#### 【CC 全文 / 詳細記錄】")
                st.write(row.get("CC全文", "尚無資料"))
                
                st.markdown("#### 【Abstract / 摘要】")
                st.caption(row.get("Abstract", "尚無資料"))

            with col2:
                st.success(f"**研究變數：**\n{row.get('研究變數(自變數、依變數、中介變數、調節變數、控制變數)', '未定義')}")
                st.warning(f"**分類標籤：** {row.get('分類標籤', '無')}")
                st.markdown(f"**研究成果：**\n{row.get('研究成果', '無')}")
                st.divider()
                st.markdown(f"**Citation:**\n`{row.get('citation', '無')}`")
            
            # 額外細節
            st.text(f"期刊名稱：{row.get('刊登期刊名稱', '不詳')}")

        st.markdown("<br>", unsafe_allow_html=True)
