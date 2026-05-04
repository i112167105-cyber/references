import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的學術文獻庫", layout="wide")

# --- 1. 請在此處替換為你剛剛複製的「2PACX」開頭的 CSV 連結 ---
CSV_URL = "這裡換成你剛剛在[發佈到網路]視窗複製的CSV連結"

@st.cache_data(ttl=60) 
def load_data():
    try:
        # 強制讀取連結並設定編碼為 utf-8
        data = pd.read_csv(CSV_URL)
        # 清除標題空格
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"連線失敗，請檢查[發佈到網路]是否選擇為「CSV」格式。錯誤訊息: {e}")
        return None

df = load_data()

st.title("📚 文獻知識庫檢索系統")

if df is not None:
    # 2. 側邊欄搜尋
    st.sidebar.header("🔍 搜尋篩選")
    search_query = st.sidebar.text_input("輸入關鍵字 (自動搜尋所有欄位)")

    # 3. 過濾邏輯
    display_df = df.copy()
    if search_query:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    st.write(f"📊 共有 {len(df)} 筆文獻 | 搜尋到 {len(display_df)} 筆")

    if display_df.empty:
        st.warning("找不到內容，請確認表格內是否有資料。")
    else:
        for _, row in display_df.iterrows():
            # 輔助函數：抓取欄位內容，若不存在則顯示無資料
            def val(col_name):
                return str(row[col_name]) if col_name in row and pd.notna(row[col_name]) else "（無資料）"

            # 顯示卡片
            title = val('篇名')
            year = val('年份')
            with st.expander(f"📖 {title} ({year})", expanded=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown("#### ✨ 文獻金句")
                    st.info(val('文獻金句/內容截錄'))
                    st.markdown("#### 📝 CC 全文 / 筆記")
                    st.write(val('CC全文'))
                    st.markdown("#### 📄 Abstract")
                    st.caption(val('Abstract'))
                with c2:
                    st.success(f"**🔬 研究變數：**\n{val('研究變數(自變數、依變數、中介變數、調節變數、控制變數)')}")
                    st.warning(f"**🏷️ 標籤：** {val('分類標籤')}")
                    st.markdown(f"**📜 Citation:**\n`{val('citation')}`")
            st.markdown("---")
