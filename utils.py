import streamlit as st
import folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from wordcloud import WordCloud
from collections import Counter
import re
from nltk.corpus import stopwords
import nltk



def create_folium_map(geo_data, coord, center=[55.74921, 37.79765], zoom=10, radius=12, blur=4, min_opacity=0.5):
    m = folium.Map(location=center, zoom_start=zoom)

    folium.GeoJson(geo_data, name="GeoJSON Layer", style_function=lambda x: {"color": "blue", "fillOpacity":0, "weight": 1}).add_to(m)
    HeatMap(coord, radius=radius, blur=blur, min_opacity=min_opacity).add_to(m)
    Fullscreen(position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True).add_to(m)
    folium.LayerControl().add_to(m)

    return st_folium(m, width=1900)


def get_average_salary_by_profession(df):
    ordered_roles = df.groupby("Профессиональная роль")["Зарплата от"].mean().sort_values(ascending=False).index

    g = sns.catplot(
        data=df,
        x="Зарплата от",
        y="Профессиональная роль",
        kind="bar",
        height=8,
        aspect=1,
        palette="rocket",
        order=ordered_roles
        )
    ax = g.ax
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5))
    plt.title("Средние зарплаты по специализациям")
    st.pyplot(g)


def get_top_companies_by_salary(df):
    df_salary_by_top10company = df[['Название компании', 'Зарплата от']].loc[df['Курс валюты'] == 'RUR'].dropna().groupby('Название компании').mean()
    df_salary_by_top10company = df_salary_by_top10company.sort_values('Зарплата от', ascending=False)[:10]
    g = sns.catplot(
        data=df[df['Название компании'].isin(df_salary_by_top10company.index)].sort_values('Зарплата от', ascending=False),
        x="Зарплата от",
        y="Название компании",
        kind="bar",
        height=8,
        aspect=1,
        hue="Название компании",
        palette="rocket"
    )
    ax = plt.gca()  # Получаем текущие оси
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
    plt.title("Компании, которые в среднем больше предлагают за вакансию")
    st.pyplot(g)


def get_top_companies_by_count_of_vacancies(df):
    df_count_by_top10company = df['Название компании'].value_counts()[:10]
    g = sns.catplot(
        x=df_count_by_top10company.values,
        y=df_count_by_top10company.index,
        kind="bar",
        height=8,
        aspect=1,
        hue=df_count_by_top10company.index,
        palette="rocket"
    )

    ax = g.ax
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))

    plt.title("Топ 10 нанимающих компаний")
    plt.xlabel("Кол-во вакансий")
    st.pyplot(g)


def get_wordcloud_request_company(df):
    text = ' '.join(df['Требования'].dropna())
    cleaned_text = re.sub(r'[\W\d_]+', ' ', text)
    nltk.download('stopwords')
    stop_words = set(stopwords.words('russian'))

    filtered_words = [word.lower() for word in cleaned_text.split() if word.lower() not in stop_words]
    word_counts = Counter(filtered_words)

    top_10_words = {word for word, _ in word_counts.most_common(10)}
    filtered_words_final = [word for word in filtered_words if word not in top_10_words]

    filtered_text = ' '.join(filtered_words_final)

    wordcloud = WordCloud(width=1200, height=800, background_color='white', colormap='viridis').generate(filtered_text)

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')  

    st.pyplot(fig) 


def get_wordcloud_responsibility_company(df):
    text = ' '.join(df['Ответственность'].dropna())
    cleaned_text = re.sub(r'[\W\d_]+', ' ', text)
    nltk.download('stopwords')
    stop_words = set(stopwords.words('russian'))

    filtered_words = [word.lower() for word in cleaned_text.split() if word.lower() not in stop_words]
    word_counts = Counter(filtered_words)

    top_10_words = {word for word, _ in word_counts.most_common(10)}
    filtered_words_final = [word for word in filtered_words if word not in top_10_words]

    filtered_text = ' '.join(filtered_words_final)

    wordcloud = WordCloud(width=1200, height=800, background_color='white', colormap='inferno').generate(filtered_text)

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    st.pyplot(fig)