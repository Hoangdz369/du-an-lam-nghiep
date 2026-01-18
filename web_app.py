import streamlit as st
import pandas as pd
import sqlite3
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Quản lý Lâm Nghiệp", layout="wide", page_icon="🌲")
db_file = "lam_nghiep.db"

# --- 1. CÁC HÀM XỬ LÝ DATABASE (Backend) ---
def get_connection():
    return sqlite3.connect(db_file)

# Lấy danh sách Huyện từ bảng hành chính
def lay_ds_huyen():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ten_huyen FROM danh_sach_hanh_chinh")
        data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data
    except:
        return []

# Lấy danh sách Xã theo Huyện
def lay_ds_xa(ten_huyen):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ten_xa FROM danh_sach_hanh_chinh WHERE ten_huyen = ?", (ten_huyen,))
        data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data
    except:
        return []

# Lấy toàn bộ dữ liệu lâm nghiệp
def load_data():
    conn = get_connection()
    # Lấy thêm cột ID để phục vụ Sửa/Xóa
    df = pd.read_sql_query("SELECT * FROM du_lieu_lam_nghiep ORDER BY id DESC", conn)
    conn.close()
    return df

# Lấy chi tiết 1 bản ghi dựa vào ID (để đổ vào form Sửa)
def lay_chi_tiet_theo_id(id_can_tim):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM du_lieu_lam_nghiep WHERE id = {id_can_tim}", conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

# --- HÀM THÊM - SỬA - XÓA ---
def them_moi_sql(params):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """INSERT INTO du_lieu_lam_nghiep 
        (huyen, xa, nam, rung_phong_ho, rung_dac_dung, rung_san_xuat, san_luong_go, ty_le_che_phu, ket_qua_trong_rung)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True, "✅ Thêm mới thành công!"
    except Exception as e:
        return False, f"❌ Lỗi: {e}"

def cap_nhat_sql(id_can_sua, params):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """UPDATE du_lieu_lam_nghiep SET 
        huyen=?, xa=?, nam=?, rung_phong_ho=?, rung_dac_dung=?, rung_san_xuat=?, 
        san_luong_go=?, ty_le_che_phu=?, ket_qua_trong_rung=? WHERE id=?"""
        # Thêm ID vào cuối danh sách tham số
        params_with_id = params + (id_can_sua,)
        cursor.execute(query, params_with_id)
        conn.commit()
        conn.close()
        return True, "✅ Cập nhật thành công!"
    except Exception as e:
        return False, f"❌ Lỗi: {e}"

def xoa_sql(id_can_xoa):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM du_lieu_lam_nghiep WHERE id = ?", (id_can_xoa,))
        conn.commit()
        conn.close()
        return True, "✅ Đã xóa bản ghi!"
    except Exception as e:
        return False, f"❌ Lỗi: {e}"

# --- 2. GIAO DIỆN CHÍNH (Frontend) ---
st.title("🌲 HỆ THỐNG QUẢN LÝ LÂM NGHIỆP ONLINE")

# Menu điều hướng bên trái
menu = st.sidebar.radio("Chức năng", ["📊 Dashboard (Xem)", "✍️ Thêm mới", "🛠️ Quản lý (Sửa/Xóa)"])

# --- TAB 1: DASHBOARD ---
if menu == "📊 Dashboard (Xem)":
    st.header("Tổng quan dữ liệu")
    df = load_data()
    
    # Bộ lọc nhanh
    ds_huyen = lay_ds_huyen()
    filter_huyen = st.multiselect("Lọc theo Huyện:", ds_huyen)
    
    if filter_huyen:
        df = df[df['huyen'].isin(filter_huyen)]
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng số bản ghi", len(df))
    col2.metric("Tổng diện tích rừng", f"{df[['rung_phong_ho', 'rung_dac_dung', 'rung_san_xuat']].sum().sum():,.0f} ha")
    col3.metric("Tổng sản lượng gỗ", f"{df['san_luong_go'].sum():,.0f} m3")
    
    st.dataframe(df, use_container_width=True)

# --- TAB 2: THÊM MỚI (Đã sửa lỗi Cascading) ---
elif menu == "✍️ Thêm mới":
    st.header("Thêm dữ liệu mới")
    
    col_a, col_b = st.columns(2)
    
    # --- PHẦN 1: CHỌN HUYỆN XÃ (Để ở ngoài để tự động load lại trang) ---
    ds_huyen = lay_ds_huyen()
    # index=0 nghĩa là mặc định chọn cái đầu tiên
    chon_huyen = col_a.selectbox("Chọn Huyện", ds_huyen, key="add_huyen")
    
    ds_xa = lay_ds_xa(chon_huyen)
    chon_xa = col_b.selectbox("Chọn Xã", ds_xa, key="add_xa")
    
    st.write("---") # Đường kẻ ngang phân cách
    
    # --- PHẦN 2: NHẬP SỐ LIỆU ---
    col1, col2 = st.columns(2)
    v_nam = col1.number_input("Năm", 2000, 2030, 2024, key="add_nam")
    v_phongho = col2.number_input("Rừng phòng hộ (ha)", 0.0, key="add_ph")
    v_dacdung = col1.number_input("Rừng đặc dụng (ha)", 0.0, key="add_dd")
    v_sanxuat = col2.number_input("Rừng sản xuất (ha)", 0.0, key="add_sx")
    v_go = col1.number_input("Sản lượng gỗ (m3)", 0.0, key="add_go")
    v_chephu = col2.slider("Tỷ lệ che phủ (%)", 0.0, 100.0, 40.0, key="add_cp")
    v_trongrung = col1.number_input("Kết quả trồng rừng (ha)", 0.0, key="add_tr")
    
    # Nút Lưu (Dùng button thường, không dùng form_submit_button nữa)
    if st.button("Lưu dữ liệu mới 💾", type="primary"):
        if not chon_huyen or not chon_xa:
             st.error("Vui lòng kiểm tra lại Huyện và Xã!")
        else:
            params = (chon_huyen, chon_xa, v_nam, v_phongho, v_dacdung, v_sanxuat, v_go, v_chephu, v_trongrung)
            ok, msg = them_moi_sql(params)
            if ok:
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)

# --- TAB 3: QUẢN LÝ (SỬA / XÓA) ---
elif menu == "🛠️ Quản lý (Sửa/Xóa)":
    st.header("Chỉnh sửa dữ liệu")
    
    df = load_data()
    st.dataframe(df.head(5), use_container_width=True)
    st.info("💡 Nhìn bảng trên để lấy ID bản ghi cần sửa/xóa")
    
    list_id = df['id'].tolist()
    id_chon = st.selectbox("Chọn ID bản ghi cần Sửa/Xóa:", list_id)
    
    if id_chon:
        record = lay_chi_tiet_theo_id(id_chon)
        
        if record is not None:
            st.write("---")
            st.subheader(f"Đang sửa bản ghi ID: {id_chon}")
            
            col_x, col_y = st.columns(2)
            
            # --- LOGIC CASCADING CHO PHẦN SỬA ---
            ds_huyen = lay_ds_huyen()
            
            # Tìm vị trí của huyện cũ trong danh sách mới
            try:
                index_huyen_cu = ds_huyen.index(record['huyen'])
            except:
                index_huyen_cu = 0
            
            # Selectbox Huyện
            u_huyen = col_x.selectbox("Huyện", ds_huyen, index=index_huyen_cu, key="edit_huyen")
            
            # Selectbox Xã (Tự động cập nhật theo u_huyen vừa chọn)
            ds_xa = lay_ds_xa(u_huyen)
            
            # Logic thông minh: 
            # Nếu huyện vẫn là huyện cũ -> Chọn xã cũ.
            # Nếu người dùng đổi huyện mới -> Chọn xã đầu tiên của huyện mới (index 0).
            try:
                if u_huyen == record['huyen']:
                     index_xa_cu = ds_xa.index(record['xa'])
                else:
                     index_xa_cu = 0
            except:
                index_xa_cu = 0
                
            u_xa = col_y.selectbox("Xã", ds_xa, index=index_xa_cu, key="edit_xa")
            
            # Các ô nhập liệu khác
            u_nam = col_x.number_input("Năm", value=int(record['nam']), key="edit_nam")
            u_phongho = col_y.number_input("Phòng hộ", value=float(record['rung_phong_ho']), key="edit_ph")
            u_dacdung = col_x.number_input("Đặc dụng", value=float(record['rung_dac_dung']), key="edit_dd")
            u_sanxuat = col_y.number_input("Sản xuất", value=float(record['rung_san_xuat']), key="edit_sx")
            u_go = col_x.number_input("Gỗ (m3)", value=float(record['san_luong_go']), key="edit_go")
            u_chephu = col_y.slider("Che phủ (%)", 0.0, 100.0, float(record['ty_le_che_phu']), key="edit_cp")
            u_trongrung = col_x.number_input("Trồng rừng", value=float(record['ket_qua_trong_rung']), key="edit_tr")
            
            col_btn1, col_btn2 = st.columns([1, 4])
            
            if col_btn1.button("Cập nhật 💾", type="primary"):
                params = (u_huyen, u_xa, u_nam, u_phongho, u_dacdung, u_sanxuat, u_go, u_chephu, u_trongrung)
                ok, msg = cap_nhat_sql(id_chon, params)
                if ok:
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
            
            with col_btn2:
                with st.expander("🗑️ Muốn xóa dòng này?"):
                    st.warning(f"Bạn có chắc muốn xóa bản ghi ID: {id_chon} không?")
                    if st.button("Xác nhận XÓA VĨNH VIỄN"):
                        ok, msg = xoa_sql(id_chon)
                        if ok:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
