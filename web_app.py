import streamlit as st
import pandas as pd
import sqlite3

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Quản lý Lâm Nghiệp", layout="wide")
st.title("🌲 HỆ THỐNG QUẢN LÝ DỮ LIỆU LÂM NGHIỆP")
st.write("Dữ liệu được lấy trực tiếp từ Database `lam_nghiep.db`")

# --- 2. HÀM LẤY DỮ LIỆU TỪ KHO ---
# Streamlit có bộ nhớ đệm (cache), giúp load lại trang cực nhanh mà không cần connect lại db liên tục
@st.cache_data
def load_data():
    conn = sqlite3.connect("lam_nghiep.db")
    # Dùng Pandas đọc thẳng SQL ra bảng luôn (chỉ 1 dòng code!)
    df = pd.read_sql_query("SELECT * FROM du_lieu_lam_nghiep", conn)
    conn.close()
    return df

try:
    df = load_data()

    # --- 3. TẠO BỘ LỌC BÊN THANH TRÁI (SIDEBAR) ---
    st.sidebar.header("🔍 Bộ lọc dữ liệu")
    
    # Lấy danh sách huyện duy nhất để đưa vào ô chọn
    ds_huyen = df['huyen'].unique()
    chon_huyen = st.sidebar.multiselect("Chọn Huyện:", ds_huyen)

    # --- 4. XỬ LÝ LỌC ---
    if chon_huyen:
        # Nếu người dùng chọn huyện, thì lọc bảng theo huyện đó
        df_hien_thi = df[df['huyen'].isin(chon_huyen)]
    else:
        # Nếu không chọn gì thì hiện hết
        df_hien_thi = df

    # --- 5. HIỂN THỊ SỐ LIỆU TỔNG QUAN (KPI) ---
    cot1, cot2, cot3 = st.columns(3)
    cot1.metric("Tổng số bản ghi", len(df_hien_thi))
    cot2.metric("Diện tích Phòng hộ", f"{df_hien_thi['rung_phong_ho'].sum():,.0f} ha")
    cot3.metric("Sản lượng gỗ", f"{df_hien_thi['san_luong_go'].sum():,.0f} m3")

    # --- 6. HIỂN THỊ BẢNG DỮ LIỆU ---
    st.subheader("📋 Danh sách chi tiết")
    # Cái bảng này xịn hơn Treeview nhiều: Sắp xếp, tìm kiếm, phóng to được luôn
    st.dataframe(df_hien_thi, use_container_width=True)

    # --- 7. VẼ BIỂU ĐỒ (Bonus) ---
    st.subheader("📊 Biểu đồ diện tích rừng phòng hộ theo Xã")
    if not df_hien_thi.empty:
        # Vẽ biểu đồ cột chỉ bằng 1 dòng lệnh
        st.bar_chart(df_hien_thi, x="xa", y="rung_phong_ho")
    else:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")

except Exception as e:
    st.error(f"Có lỗi xảy ra: {e}. Bạn đã copy file 'lam_nghiep.db' vào cùng thư mục chưa?")