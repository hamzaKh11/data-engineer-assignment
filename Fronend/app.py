import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

# FastAPI endpoint
API_URL = "http://localhost:8000"


def fetch_articles():
    response = requests.get(f"{API_URL}/articles")
    return response.json()


def classify_custom_categories(submenu):
    # Define your custom category mapping here
    submenu_to_category = {
        "Football": "Sports",
        "Tennis": "Sports",
        "Formula 1": "Sports",
        "Rugby U": "Sports",
        "Athletics": "Sports",
        "Cricket": "Sports",
        "Cycling": "Sports",
        "Golf": "Sports",
        "Israel-Gaza War": "War and Conflict",
        "Film & TV": "Entertainment",
        "Music": "Entertainment",
        "Art & Design": "Entertainment",
        "Style": "Entertainment",
        "Science & Health": "Science and Health",
        "Books": "Entertainment",
        "Entertainment News": "Entertainment",
        "World’s Table": "Culture and Society",
        "Culture & Experiences": "Culture and Society",
        "Adventures": "Culture and Society",
        "The SpeciaList": "Culture and Society",
        "Natural Wonders": "Environment and Sustainability",
        "Weather & Science": "Environment and Sustainability",
        "Climate Solutions": "Environment and Sustainability",
        "Sustainable Business": "Business and Finance",
        "Artificial Intelligence": "Technology",
        "Future of Business": "Business and Finance",
        "Technology": "Technology",
        "Work Culture": "Culture and Society",
        "Technology of Business": "Business and Finance",
        "War in Ukraine": "War and Conflict",
        "BBC Verify": "Media",
        "In Pictures": "Entertainment",
        "Middle East": "International Relations",
        "Latin America": "International Relations",
        "Europe": "International Relations",
        "Australia": "International Relations",
        "Asia": "International Relations",
        "Africa": "International Relations",
        "UK": "International Relations",
        "US & Canada": "International Relations",
        "UK General Election": "Politics and Governance",
        "Green Living": "Environment and Sustainability"
    }
    return submenu_to_category.get(submenu, "Other")


def main():
    st.title("BBC Analysis Platform")
    st.sidebar.title("Menu")
    menu = st.sidebar.selectbox(
        "Select an option", ["Home", "Analysis"])

    if menu == "Home":
        st.header("All Articles")
        articles = fetch_articles()
        for article in articles:
            st.subheader(article['Title'])
            st.text(article['Subtitle'])
            st.text(f"Authors: {', '.join(article['Authors'])}")
            st.text(f"Published Date: {article['date_published']}")
            st.markdown(article['Text'])
            if article.get('Images') and article['Images']:
                try:
                    st.image(article['Images'][0])
                except FileNotFoundError:
                    st.write("Image not found")
            else:
                st.write("No image available")
            st.markdown("""---""")

    elif menu == "Analysis":
        st.header("Data Analysis")
        articles = fetch_articles()
        df = pd.DataFrame(articles)

        # Number of articles per topic
        st.write("Number of articles per topic:")
        topic_counts = df.explode('Topics')['Topics'].value_counts()
        st.bar_chart(topic_counts)

        # Number of articles per menu
        st.write("Number of articles per menu:")
        menu_counts = df['Menu'].value_counts()
        st.bar_chart(menu_counts)

        # Additional analysis as per the questions

        # Bias detection
        st.write("Bias detection:")
        # Calculate bias by comparing the frequency of topics
        most_common_topic = topic_counts.idxmax()
        least_common_topic = topic_counts.idxmin()
        st.write(f"Most common topic: {most_common_topic}")
        st.write(f"Least common topic: {least_common_topic}")

        # Other extractions
        # st.write("Other extractions:")
        # You can extract more insights here, like sentiment analysis, keyword extraction, etc.

        # Categorization based on relevance or similarity
        st.write("Categorization based on relevance or similarity:")
        # Use TF-IDF and cosine similarity to categorize articles
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['Text'])
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        # Example: Clustering using KMeans
        num_clusters = 3  # Define the number of clusters
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(tfidf_matrix)
        clusters = kmeans.labels_
        df['Cluster'] = clusters
        # Display article titles with their respective clusters
        st.write(df[['Title', 'Cluster']])

        # Classification into custom categories
        st.write("Classification into custom categories:")
        df['Custom Category'] = df['Submenu'].apply(classify_custom_categories)
        st.write(df[['Title', 'Custom Category']])

    # Add more elif conditions for other menu options if needed


if __name__ == "__main__":
    main()
