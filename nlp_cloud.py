# 📦 Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS

# 🎨 App Header
st.set_page_config(page_title="Word Cloud Generator", layout="centered")
st.title("🌀 Simple Streamlit App: Word Cloud Visualizer")

st.markdown(""" 
Visualize webpage content as a Word Cloud  
* **Libraries Used:** Streamlit, BeautifulSoup, WordCloud, PIL  
* **Contact:** [Seaport.ai](https://seaportai.com/contact-us)  
""")

# 🧮 Sidebar Settings
st.sidebar.header("⚙️ Settings")
task = st.sidebar.radio("Select Link Type", ["Use Predefined Link", "Enter Custom Link"])

predefined_links = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.geeksforgeeks.org/machine-learning/what-is-reinforcement-learning/"
]

selected_link = st.sidebar.selectbox("Choose a predefined link", predefined_links) if task == "Use Predefined Link" else None
custom_link = st.sidebar.text_input("Paste your own link") if task == "Enter Custom Link" else None
final_url = custom_link if custom_link else selected_link

word_limit = st.sidebar.slider("Max Word Count", 100, 1000, 400, step=100)

# 🎭 Shape Selection Logic
st.sidebar.header("🖼️ Shape Selection")
shape_mode = st.sidebar.radio("Select Shape Source", ["Use Built-in Shape", "Upload Custom Image"])

mask_image = None
if shape_mode == "Use Built-in Shape":
    shape_choice = st.sidebar.selectbox("Choose Shape", ["Circle", "Star", "Heart", "Unique 01"], placeholder="Select here")

    shape_paths = {
        "Circle": "shapes/circle.png",
        "Star": "shapes/star.png",
        "Heart": "shapes/heart.png",
        "Unique 01": "shapes/unique.png"
    }
    try:
        mask_image = np.array(Image.open(shape_paths[shape_choice]))
        st.sidebar.info(f"🎭 Loaded built-in shape: {shape_choice}")
    except Exception as e:
        st.sidebar.warning(f"❌ Couldn't load shape image: {e}")
else:
    uploaded_file = st.sidebar.file_uploader("Upload Shape Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        try:
            mask_image = np.array(Image.open(uploaded_file))
            st.sidebar.success("🖼️ Custom image loaded successfully!")
        except Exception as e:
            st.sidebar.warning(f"Error loading uploaded image: {str(e)}")
            
# 🌐 Fetch and Process Web Content
if st.sidebar.button("Generate Word Cloud") and final_url:
    try:
        response = requests.get(final_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unnecessary tags
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()

        content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or \
                soup.find('div', id='main') or soup.find('body')

        if content:
            raw_text = content.get_text()
            cleaned_text = re.sub(r'\s+', ' ', raw_text)
            cleaned_text = re.sub(r'\[\d+\]', '', cleaned_text)

            st.subheader("📖 Preview of Extracted Content")
            st.text(cleaned_text[:500] + "..." if cleaned_text else "No visible text found.")

            # 🌈 Word Cloud Generation
            st.subheader("🌟 Word Cloud Output")
            with st.spinner("Creating word cloud..."):
                wc = WordCloud(
                    background_color="white",
                    max_words=word_limit,
                    stopwords=set(STOPWORDS),
                    mask=mask_image,
                    contour_color="black",
                    contour_width=1 if mask_image is not None else 0
                ).generate(cleaned_text)

                fig, axis = plt.subplots(figsize=(10, 6))
                axis.imshow(wc, interpolation='bilinear')
                axis.axis("off")
                st.pyplot(fig)

            # 📥 Download Button
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            st.download_button(
                label="Download Word Cloud",
                data=img_buffer.getvalue(),
                file_name="wordcloud.png",
                mime="image/png"
            )
        else:
            st.error("⚠️ Couldn't find usable content. Try a different link or page structure.")
    except requests.exceptions.RequestException as e:
        st.error(f"🧨 Request error: {e}")
    except Exception as e:
        st.error(f"😢 Something went wrong: {e}")
elif not final_url:
    st.warning("🔗 Please enter or select a valid URL.")
