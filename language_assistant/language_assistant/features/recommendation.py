import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Step 1: Load data
conn = sqlite3.connect("users.db")
df = pd.read_sql_query("SELECT * FROM learning_history", conn)
conn.close()

# Step 2: Clean data
df.dropna(subset=['quiz_score', 'total_questions'], inplace=True)
df['quiz_percentage'] = (df['quiz_score'] / df['total_questions']) * 100

# Step 3: Create pivot table
pivot_df = df.pivot_table(index='username', columns='lesson_name', values='quiz_percentage').fillna(0)

# Step 4: Normalize scores
scaler = StandardScaler()
normalized_scores = scaler.fit_transform(pivot_df)

# Step 5: Fit Nearest Neighbors model
model = NearestNeighbors(metric='cosine', algorithm='brute')
model.fit(normalized_scores)


# Step 6: Hybrid Recommender Function
def recommend_lessons_hybrid(username, weak_threshold=60, similar_user_threshold=70, n_recommendations=5):
    if username not in pivot_df.index:
        return ["User not found"]

    user_index = list(pivot_df.index).index(username)
    num_users = len(pivot_df)

    recommendations = []

    if num_users > 1:
        n_neighbors = min(4, num_users)
        distances, indices = model.kneighbors([normalized_scores[user_index]], n_neighbors=n_neighbors)

        similar_users = [pivot_df.index[i] for i in indices.flatten() if i != user_index]
        user_lessons = set(df[df['username'] == username]['lesson_name'])
        weak_lessons = df[(df['username'] == username) & (df['quiz_percentage'] < weak_threshold)]['lesson_name'].tolist()

        for similar_user in similar_users:
            similar_user_data = df[df['username'] == similar_user]
            high_scores = similar_user_data[similar_user_data['quiz_percentage'] >= similar_user_threshold]

            for lesson in high_scores['lesson_name']:
                if lesson not in user_lessons and lesson not in recommendations:
                    if any(weak_key in lesson.lower() for weak_key in [w.lower() for w in weak_lessons]):
                        recommendations.insert(0, lesson)
                    else:
                        recommendations.append(lesson)
                if len(recommendations) >= n_recommendations:
                    break
            if len(recommendations) >= n_recommendations:
                break

    # If only one user or not enough recommendations, fall back to weak areas
    if len(recommendations) < n_recommendations:
        user_weak_lessons = df[(df['username'] == username) & (df['quiz_percentage'] < weak_threshold)]
        sorted_weak = user_weak_lessons.sort_values('quiz_percentage')["lesson_name"].tolist()
        for lesson in sorted_weak:
            if lesson not in recommendations:
                recommendations.append(lesson)
            if len(recommendations) >= n_recommendations:
                break

    return recommendations or ["No new recommendations (try adding more data)"]


def get_db_connection():
    conn = sqlite3.connect("users.db")
    return conn


def get_user_data(username):
    conn = get_db_connection()
    user_history = pd.read_sql_query(f"""
        SELECT * FROM learning_history 
        WHERE username = '{username}'
        ORDER BY date_completed DESC
    """, conn)
    conn.close()
    return user_history


def user_dashboard(username):
    user_history = get_user_data(username)
    user_history.dropna(subset=['quiz_score', 'total_questions'], inplace=True)
    user_history['quiz_percentage'] = (user_history['quiz_score'] / user_history['total_questions']) * 100
    recommendations = recommend_lessons_hybrid(username)

    st.title("Personalized Learning Dashboard")
    st.title(f"Welcome, {username}")

    total_lessons = len(user_history)
    avg_score = user_history['quiz_percentage'].mean()
    last_activity = user_history['date_completed'].max()

    st.metric("Total Lessons Completed", total_lessons)
    st.metric("Average Score", f"{avg_score:.1f}%" if not pd.isnull(avg_score) else "N/A")
    st.metric("Last Active", last_activity if last_activity else "N/A")

    st.divider()
    st.write("**Quick Actions**")
    if st.button("Refresh Recommendations"):
        st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.pie(user_history, names='lesson_name', title='Lessons Distribution')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(user_history, x='quiz_percentage', title='Score Distribution')
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        progress_df = user_history.copy()
        progress_df['date_completed'] = pd.to_datetime(progress_df['date_completed'])
        progress_df = progress_df.groupby('date_completed').size().cumsum().reset_index(name='Total Lessons')
        fig = px.line(progress_df, x='date_completed', y='Total Lessons', title='Learning Progress Over Time')
        st.plotly_chart(fig, use_container_width=True)

    st.header("📉 Areas Needing Improvement")
    weak_lessons = user_history[user_history['quiz_percentage'] < 60]

    if not weak_lessons.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Lowest Scoring Lessons")
            weak_df = weak_lessons.sort_values('quiz_percentage').head(5)[['lesson_name', 'quiz_percentage']]
            st.dataframe(weak_df.style.highlight_min(axis=0, color='blue'), hide_index=True, use_container_width=True)

        with col2:
            st.subheader("Weak Categories")
            weak_categories = weak_lessons['lesson_name'].value_counts().head(5)
            fig = px.bar(weak_categories, orientation='h', labels={'value': 'Count', 'index': 'Lesson'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("🎉 Great job! No weak areas detected based on your threshold.")

    st.header("🎯 Recommended Next Lessons")
    if isinstance(recommendations, list) and recommendations[0] != "No new recommendations":
        cols = st.columns(min(3, len(recommendations)))
        for idx, lesson in enumerate(recommendations):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="border-radius: 10px; padding: 15px; margin-bottom: 15px; ">
                    <h4>{lesson}</h4>
                    <p>Recommended based on your learning patterns</p>
                    <button style="background-color: #4CAF50; color: white; border: none; padding: 8px 16px; text-align: center; 
                    text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">
                    Start Learning</button>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning(recommendations[0])

    st.header("🕒 Recent Activity")
    st.dataframe(user_history.head(10),
                 column_config={
                     "date_completed": "Date",
                     "lesson_name": "Lesson",
                     "quiz_percentage": st.column_config.ProgressColumn(
                         "Score",
                         help="Your quiz score",
                         format="%d%%",
                         min_value=0,
                         max_value=100,
                     ),
                     "completion_time": "Duration (min)"
                 },
                 hide_index=True, use_container_width=True)
