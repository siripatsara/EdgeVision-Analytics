import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from urllib.request import urlopen

st.set_page_config(page_title="Image Processing Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>Image Processing with Streamlit</h1>",
            unsafe_allow_html=True)

# 1. เลือกแหล่งที่มาของภาพ
source = st.radio("เลือกแหล่งที่มาของภาพ", ["Webcam", "URL"])

# โหลดภาพ
img = None
if source == "Webcam":
    img_file_buffer = st.camera_input("สั่งเปิดเว็บแคม")
    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        img = cv2.imdecode(np.frombuffer(
            bytes_data, np.uint8), cv2.IMREAD_COLOR)

elif source == "URL":
    url = st.text_input("กรอก URL ของภาพ",
                        "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg")
    if st.button("โหลดภาพ"):
        try:
            resp = urlopen(url)
            img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:
            st.error(f"โหลดภาพล้มเหลว: {e}")

# 2. ถ้ามีภาพแล้ว
if img is not None:
    st.subheader("ตั้งค่า Image Processing")

    gray = st.checkbox("แปลงเป็น Grayscale")
    blur_ksize = st.slider(
        "Blur kernel size (ค่าควรเป็นเลขคี่)", 1, 31, 5, step=2)
    canny_low = st.slider("Canny Edge — Low threshold", 50, 200, 100)
    canny_high = st.slider("Canny Edge — High threshold", 100, 300, 200)

    processed = img.copy()
    if gray:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    processed = cv2.GaussianBlur(processed, (blur_ksize, blur_ksize), 0)
    processed = cv2.Canny(processed, canny_low, canny_high)

    col1, col2 = st.columns(2)
    with col1:
        st.image(processed, caption="Processed Image", use_column_width=True)
    with col2:
        st.subheader("Data Visualization")

        # เลือกประเภทกราฟ
        chart_type = st.selectbox("เลือกประเภทกราฟ", [
            "Histogram",
            "Edge Count Summary",
            "Image Statistics",
            "Intensity Distribution (Box Plot)",
            "Line Plot"
        ])

        fig, ax = plt.subplots(figsize=(8, 6))

        if chart_type == "Histogram":
            if len(processed.shape) == 2:
                ax.hist(processed.ravel(), bins=50, color='skyblue',
                        alpha=0.7, edgecolor='black')
                ax.set_title("Histogram (Grayscale / Edges)")
                ax.set_xlabel("Intensity value")
                ax.set_ylabel("Count")
            else:
                ax.set_title("Color Histogram not supported for edges")

        elif chart_type == "Edge Count Summary":
            edge_pixels = np.sum(processed == 255)
            non_edge_pixels = np.sum(processed == 0)

            labels = ['Background\n(Non-Edge)', 'Edge Pixels']
            sizes = [non_edge_pixels, edge_pixels]
            colors = ['lightcoral', 'lightblue']

            ax.pie(sizes, labels=labels, colors=colors,
                   autopct='%1.1f%%', startangle=90)
            ax.set_title('Edge vs Background Pixels')

        elif chart_type == "Image Statistics":
            stats = {
                'Mean': np.mean(processed),
                'Std Dev': np.std(processed),
                'Min': np.min(processed),
                'Max': np.max(processed),
                'Edge Count': np.sum(processed == 255)
            }

            bars = ax.bar(stats.keys(), stats.values(), color=[
                          'red', 'green', 'blue', 'orange', 'purple'])
            ax.set_title('Image Processing Statistics')
            ax.set_ylabel('Value')

            # เพิ่มตัวเลขบนแท่ง
            for bar, value in zip(bars, stats.values()):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                        f'{value:.1f}', ha='center', va='bottom')

        elif chart_type == "Intensity Distribution (Box Plot)":
            ax.boxplot(processed.ravel(), vert=True)
            ax.set_title('Intensity Value Distribution')
            ax.set_ylabel('Intensity Value')
            ax.set_xticklabels(['Processed Image'])

        elif chart_type == "Line Plot":
            # แสดง intensity profile แถวกลางของภาพ
            middle_row = processed[processed.shape[0]//2, :]
            ax.plot(middle_row, color='blue', linewidth=2)
            ax.set_title('Intensity Profile (Middle Row)')
            ax.set_xlabel('Pixel Position')
            ax.set_ylabel('Intensity Value')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
