import streamlit as st
import pandas as pd

# 頁面基本設定
st.set_page_config(page_title="文獻知識庫檢索系統", layout="wide")

# --- 1. 設定你的 Google 表格發佈連結 ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzmPx1QL1mSDlixFRWGqXuqG8308TMgub-mo0etJ2_qysm0kQJPFmAhyC7PU82IBwCPBgZyX01eE2a/pub?output=csv"

@st.cache_data(ttl=30) # 每 30 秒快取更新
def load_data():
    try:
        # 讀取 CSV 並處理可能的編碼問題
        data = pd.read_csv(CSV_URL)
        # 清除標題空格
        data.columns = data.columns.str.strip()
        # 移除完全空白的列
        data = data.dropna(how='all')
        return data
    except Exception as e:
        st.error(f"❌ 讀取資料失敗，請確認連結是否正確。錯誤訊息: {e}")
        return None

df = load_data()

# --- 2. 顯示介面 ---
st.title("📚 我的學術文獻檢索系統")

if df is not None:
    # 側邊欄：搜尋框
    st.sidebar.header("🔍 檢索中心")
    search_query = st.sidebar.text_input("輸入關鍵字 (可搜尋全文、金句、標籤、變數...)", placeholder="例如：AI、質性、中介...")

    # 執行搜尋邏輯
    display_df = df.copy()
    if search_query:
        # 同時掃描所有欄位，只要包含關鍵字就顯示
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    st.write(f"📊 目前資料庫共有 {len(df)} 筆文獻 | 搜尋結果：{len(display_df)} 筆")

    # 如果沒有搜尋結果
    if display_df.empty:
        st.warning("⚠️ 找不到符合條件的文獻內容，請嘗試其他關鍵字。")
    else:
        # 逐筆顯示文獻內容
        for _, row in display_df.iterrows():
            # 建立輔助函數來安全獲取欄位內容
            def get_val(col_name):
                return str(row[col_name]) if col_name in row and pd.notna(row[col_name]) else "（無資料）"

            # 顯示標題與年份
            with st.expander(f"📖 {get_val('篇名')} ({get_val('年份')})", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### ✨ 文獻金句 / 核心截錄")
                    st.info(get_val('文獻金句/內容截錄'))
                    
                    st.markdown("#### 📝 CC 全文 / 深入筆記")
                    st.write(get_val('CC全文'))
                    
                    st.markdown("#### 📄 Abstract / 摘要")
                    st.caption(get_val('Abstract'))
                
                with col2:
                    st.success(f"**🔬 研究變數：**\n{get_val('研究變數(自變數、依變數、中介變數、調節變數、控制變數)')}")
                    st.warning(f"**🏷️ 分類標籤：** {get_val('分類標籤')}")
                    st.markdown(f"**📜 期刊名稱：** {get_val('刊登期刊名稱')}")
                    st.divider()
                    st.markdown(f"**📖 Citation (APA):**\n`{get_val('citation')}`")
            
            # 每一篇文獻之間留一點間隔
            st.markdown("<br>", unsafe_allow_html=True)

else:
    st.info("💡 正在連線至 Google Sheets，請稍候...")
