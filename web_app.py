import streamlit as st
import pandas as pd
import sqlite3
import time

# --- CẤU HÌNH ---
st.set_page_config(page_title="Quản lý Lâm Nghiệp", layout="wide")
db_file = "lam_nghiep.db"

# --- HÀM KẾT NỐI ---
def get_connection():
    return sqlite3.connect(db_file)

# --- HÀM LẤY DỮ LIỆU ---
def load_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM du_lieu_lam_nghiep ORDER BY id DESC", conn)
    conn.close()
    return df

# --- HÀM THÊM MỚI ---
def them_moi(huyen, xa, nam, phong_ho, dac_dung, san_xuat, go, che_phu, trong_rung):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO du_lieu_lam_nghiep 
        (huyen, xa, nam, rung_phong_ho, rung_dac_dung, rung_san_xuat, san_luong_go, ty_le_che_phu, ket_qua_trong_rung)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (huyen, xa, nam, phong_ho, dac_dung, san_xuat, go, che_phu, trong_rung))
        conn.commit()
        conn.close()
        return True, "Thêm thành công!"
    except Exception as e:
        return False, str(e)

# --- GIAO DIỆN CHÍNH ---
st.title("🌲 HỆ THỐNG QUẢN LÝ DỮ LIỆU LÂM NGHIỆP")

# Tạo 2 tab: Xem dữ liệu và Nhập liệu
tab1, tab2 = st.tabs(["📊 Bảng điều khiển (Dashboard)", "✍️ Nhập liệu & Chỉnh sửa"])

# --- TAB 1: XEM DỮ LIỆU (Giống code cũ) ---
with tab1:
    df = load_data()
    # Thống kê nhanh
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng số xã", len(df))
    c1.metric("Tổng diện tích rừng", f"{df['rung_phong_ho'].sum() + df['rung_dac_dung'].sum() + df['rung_san_xuat'].sum():,.0f} ha")
    
    st.dataframe(df, use_container_width=True)

# --- TAB 2: NHẬP LIỆU (MỚI) ---
with tab2:
    st.header("Thêm dữ liệu mới")
    
    # Tạo Form nhập liệu
    with st.form("form_nhap_lieu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            inp_huyen = st.text_input("Tên Huyện")
            inp_xa = st.text_input("Tên Xã")
            inp_nam = st.number_input("Năm", min_value=2000, max_value=2030, step=1, value=2024)
        with col2:
            inp_phongho = st.number_input("Rừng phòng hộ (ha)", min_value=0.0)
            inp_dacdung = st.number_input("Rừng đặc dụng (ha)", min_value=0.0)
            inp_sanxuat = st.number_input("Rừng sản xuất (ha)", min_value=0.0)
            inp_go = st.number_input("Sản lượng gỗ (m3)", min_value=0.0)
        
        # Các chỉ số phụ
        inp_chephu = st.slider("Tỷ lệ che phủ (%)", 0.0, 100.0, 45.0)
        inp_trongrung = st.number_input("Kết quả trồng rừng (ha)", min_value=0.0)
        
        # Nút Submit
        submitted = st.form_submit_button("Lưu dữ liệu 💾")
        
        if submitted:
            if not inp_huyen or not inp_xa:
                st.error("Vui lòng nhập tên Huyện và Xã!")
            else:
                thanh_cong, thong_bao = them_moi(
                    inp_huyen, inp_xa, inp_nam, inp_phongho, 
                    inp_dacdung, inp_sanxuat, inp_go, inp_chephu, inp_trongrung
                )
                if thanh_cong:
                    st.success(thong_bao)
                    time.sleep(1) 
                    st.rerun() # Tự động tải lại trang để cập nhật bảng bên Tab 1
                else:
                    st.error(f"Lỗi: {thong_bao}")
