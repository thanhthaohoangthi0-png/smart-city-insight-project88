import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# 1. Cấu hình trang rộng để trông chuyên nghiệp hơn
st.set_page_config(page_title="Smart City Dashboard", layout="wide")

st.title("🏙️ Hệ Thống Giám Sát Đô Thị Thông Minh")
st.markdown("Dữ liệu phân tích thời gian thực về giao thông và môi trường.")

# --- SIDEBAR ---
st.sidebar.header("Bộ Lọc Dữ Liệu")
city_zone = st.sidebar.selectbox("Chọn khu vực:", ["Toàn thành phố", "Quận 1", "Quận 7", "TP. Thủ Đức"])
st.sidebar.markdown("---")
st.sidebar.write("Thiết kế bởi: [Tên của bạn]")

# --- GIẢ LẬP DỮ LIỆU ---
# Tạo 500 điểm dữ liệu ngẫu nhiên xung quanh khu vực TP.HCM
df = pd.DataFrame(
    np.random.randn(500, 2) / [50, 50] + [10.762622, 106.660172],
    columns=['lat', 'lon']
)
df['violation_level'] = np.random.randint(1, 100, 500) # Chỉ số giả lập

# --- PHẦN 1: CÁC CHỈ SỐ TỔNG QUAN ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chỉ số AQI", "75", "-5%")
col2.metric("Nhiệt độ", "31°C", "1.2°C")
col3.metric("Mật độ giao thông", "Vừa phải", "Ổn định")
col4.metric("Điểm rác thải", "12 điểm", "Tăng")

st.markdown("---")

# --- PHẦN 2: BẢN ĐỒ 3D (PYDECK) ---
st.subheader("📍 Bản đồ mật độ vi phạm giao thông (3D)")

# Cấu hình lớp hiển thị 3D (Hexagon)
layer = pdk.Layer(
    "HexagonLayer",
    df,
    get_position=["lon", "lat"],
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    elevation_range=[0, 300],
    extruded=True,
    coverage=1,
)

view_state = pdk.ViewState(latitude=10.76, longitude=106.66, zoom=12, pitch=45)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# --- PHẦN 3: BIỂU ĐỒ TƯƠNG TÁC (PLOTLY) ---
st.markdown("---")
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Xu hướng ô nhiễm theo giờ")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Bụi mịn', 'CO2', 'Tiếng ồn'])
    fig = px.line(chart_data)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("📊 Phân bổ ngân sách hạ tầng")
    pie_df = pd.DataFrame({"Hạng mục": ["Cầu đường", "Cây xanh", "Chiếu sáng"], "Ngân sách": [50, 30, 20]})
    fig_pie = px.pie(pie_df, values='Ngân sách', names='Hạng mục', hole=.3)
    st.plotly_chart(fig_pie, use_container_width=True)