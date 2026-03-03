import streamlit as st
import pandas as pd
import pickle
import re
import string
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="IMDb Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 IMDb Storyline-Based Movie Recommender")

st.markdown("Enter a movie storyline and get top 5 similar movies.")

# -------------------------------------------------
# Text Cleaning Function
# -------------------------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

# -------------------------------------------------
# Load Resources
# -------------------------------------------------
@st.cache_resource
def load_resources():
    df = pd.read_csv("imdb_movies_2024.csv")

    # Ensure correct column names
    df["Title"] = df["Title"].astype(str)
    df["Storyline"] = df["Storyline"].astype(str)

    tfidf = pickle.load(open("tfidf.pkl", "rb"))
    tfidf_matrix = pickle.load(open("tfidf_matrix.pkl", "rb"))

    return df, tfidf, tfidf_matrix

df, tfidf, tfidf_matrix = load_resources()

# -------------------------------------------------
# Recommendation Function (Based on Storyline Input)
# -------------------------------------------------
def recommend_from_storyline(user_input, top_n=5):

    cleaned_input = clean_text(user_input)

    input_vector = tfidf.transform([cleaned_input])

    similarity_scores = cosine_similarity(input_vector, tfidf_matrix)

    similarity_scores = list(enumerate(similarity_scores[0]))

    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    top_movies = similarity_scores[:top_n]

    movie_indices = [i[0] for i in top_movies]
    scores = [round(i[1], 3) for i in top_movies]

    result = df.iloc[movie_indices][["Title"]].copy()
    result["Similarity Score"] = scores

    return result

# -------------------------------------------------
# UI
# -------------------------------------------------
user_storyline = st.text_area("✍️ Enter Movie Storyline")

top_n = st.slider("Number of Recommendations", 3, 10, 5)

if st.button("🎯 Recommend Movies"):

    if user_storyline.strip() == "":
        st.warning("Please enter a storyline.")
    else:
        recommendations = recommend_from_storyline(user_storyline, top_n)

        st.subheader("✨ Top Recommended Movies")

        for _, row in recommendations.iterrows():
            st.markdown(f"""
            ### 🎥 {row['Title']}
            **Similarity Score:** {row['Similarity Score']}
            ---
            """)