import streamlit as st
import pandas as pd
import pydeck as pdk
import google.generativeai as genai
import plotly.express as px

# --- 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP (SLATE & CYAN) ---
st.set_page_config(page_title="Nghệ An Smart City Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Nền Slate tối giản, thanh lịch */
    .stApp { background-color: #0f172a; color: #f8fafc; }

    /* Tiêu đề thanh lịch có gạch chân nhẹ */
    .main-title {
        font-size: 32px; font-weight: 700; color: #38bdf8;
        text-align: left; padding: 10px 0; border-bottom: 2px solid #1e293b;
    }

    /* Làm nổi bật các số liệu (Metrics) */
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 800; }
    [data-testid="stMetric"] { background: #1e293b; padding: 15px; border-radius: 8px; }

    /* Chỉnh sidebar gọn gàng */
    [data-testid="stSidebar"] { background-color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DỮ LIỆU THỰC TẾ 5 HUYỆN ---
data_nghe_an = pd.DataFrame({
    'Huyện': ['TP. Vinh', 'Hưng Nguyên', 'Nghi Lộc', 'Đô Lương', 'Nam Đàn'],
    'lat': [18.6734, 18.6815, 18.7512, 18.9000, 18.7000],
    'lon': [105.6813, 105.5821, 105.6214, 105.3000, 105.5000],
    'AQI': [72, 55, 58, 48, 52],
    'Nhiet_do': [24, 23, 23, 22, 22],
    'Ngan_sach': [500, 150, 200, 180, 120]  # Đơn vị: Triệu VND
})

# Sidebar quản trị
st.sidebar.markdown("### 🛠️ QUẢN TRỊ DỰ ÁN")
st.sidebar.info("Tác giả: Hoàng Thị Thanh Thảo")
st.sidebar.write("Trạng thái hệ thống: **Live**")

st.markdown('<div class="main-title">🏙️ HỆ THỐNG GIÁM SÁT THÔNG MINH TỈNH NGHỆ AN</div>', unsafe_allow_html=True)

# --- 3. KHU VỰC CÁC CHỈ SỐ NHANH (METRICS) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("AQI Cao nhất (Vinh)", "72", "Cảnh báo")
m2.metric("Nhiệt độ TB", "22.8 °C", "Ổn định")
m3.metric("Số huyện", "5", "Đã kết nối")
m4.metric("Trạng thái AI", "Sẵn sàng", "Xác thực")

st.markdown("---")

# --- 4. KHU VỰC BIỂU ĐỒ (GIẢI QUYẾT SỰ LẠC QUẺ) ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 So sánh Chỉ số AQI")
    fig_bar = px.bar(data_nghe_an, x='Huyện', y='AQI',
                     color_discrete_sequence=['#0ea5e9'], template="plotly_dark")
    fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("💰 Phân bổ Ngân sách Hạ tầng")
    fig_pie = px.pie(data_nghe_an, values='Ngan_sach', names='Huyện',
                     hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r, template="plotly_dark")
    fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 5. BẢN ĐỒ CHÍNH (3D VISUALIZATION) ---
st.subheader("📍 Bản đồ Mật độ 3D Không gian thực")
view_state = pdk.ViewState(latitude=18.78, longitude=105.48, zoom=8.8, pitch=50)

layer = pdk.Layer(
    "ColumnLayer",
    data_nghe_an,
    get_position=['lon', 'lat'],
    get_elevation='AQI',
    elevation_scale=150,
    radius=2200,
    get_fill_color=[56, 189, 248, 200],  # Màu xanh Cyan tinh tế
    pickable=True,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip={"text": "{Huyện}: AQI {AQI}"}
))

# --- 6. PHẦN CHATBOT (PHIÊN BẢN VẠN NĂNG - TỰ ĐỘNG DÒ TÌM MODEL) ---
st.divider()
st.subheader("🤖 Trợ lý AI (Hệ thống phân tích chuyên sâu)")

genai.configure(api_key="AIzaSyAzfz7kTTIbWQpUHRWvAwLb-C6H0KE-gQs")

@st.cache_resource
def find_any_model():
    try:
        # Lấy danh sách tất cả các model mà API Key này hỗ trợ
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            # Ưu tiên lấy flash nếu có, không thì lấy cái đầu tiên trong danh sách
            target = next((m for m in available_models if "flash" in m), available_models[0])
            return genai.GenerativeModel(target)
    except Exception as e:
        st.error(f"Lỗi truy xuất danh sách Model: {e}")
    return None

model = find_any_model()

if model is None:
    st.warning("⚠️ Không tìm thấy mô hình AI nào khả dụng. Vui lòng kiểm tra lại API Key hoặc chạy lệnh 'pip install -U google-generativeai' lần cuối.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Hỏi tôi về nhiệt độ, AQI hoặc ngân sách..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"Dữ liệu Nghệ An hiện tại: {data_nghe_an.to_string(index=False)}."
            try:
                response = model.generate_content(f"{context}\n\nCâu hỏi: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ Trợ lý gặp lỗi khi trả lời: {e}")