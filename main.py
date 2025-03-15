import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid
import numpy as np
import datetime
from utils import (create_folium_map, get_average_salary_by_profession,
                  get_top_companies_by_salary, get_top_companies_by_count_of_vacancies,
                  get_wordcloud_request_company, get_wordcloud_responsibility_company)

from parsing_data import get_df, get_list, get_vacancies

st.set_page_config(layout="wide")

roles_str = '157&156&160&10&150&25&165&36&96&164&104&112&113&148&114&124&125'
professional_roles = roles_str.replace('&', ',').split(',')

now = datetime.datetime.now()
date_to = now.strftime("%Y-%m-%d")
week_ago = now - datetime.timedelta(weeks=1)  
date_from = week_ago.strftime("%Y-%m-%d")  

lst = get_list(professional_roles, date_from, date_to)
df = get_df(lst)

#df = pd.read_csv("hh_data_coord.csv", index_col=0)
df['До вычета налогов'] = df['До вычета налогов'].apply(lambda x: str(x) if pd.notnull(x) else None)

geojson_path = 'ao.geojson'
with open(geojson_path, 'r', encoding='utf-8') as f:
    geo_data = json.load(f)

wage = st.slider("What is your lower salary target?", int(df['Зарплата от'].min()), 
                int(df['Зарплата от'].max()), (int(np.percentile(df['Зарплата от'].dropna(), 25)), 
                int(np.percentile(df['Зарплата от'].dropna(), 75))))

"---"

filtered_df = df.loc[(df['Зарплата от'] >= wage[0]) & 
                          (df['Зарплата от'] <= wage[1])]

col1, col2 = st.columns(2)

with col1:
    specialization = st.selectbox("What specialization are you looking for?",
                                tuple(['All specialization']+ filtered_df['Профессиональная роль'].unique().tolist()))
    if specialization != 'All specialization':
        filtered_df = filtered_df[filtered_df['Профессиональная роль'] == specialization]
with col2:
    experience = st.selectbox("What level of competence do you have?",
                          tuple(['Irrelevant'] + filtered_df['Опыт работы'].unique().tolist()))
    if experience != 'Irrelevant':
        filtered_df = filtered_df[filtered_df['Опыт работы'] == experience]

AgGrid(filtered_df[['Название вакансии', 'Название компании', 'Зарплата от', 'Зарплата до',  
            'Курс валюты', 'До вычета налогов', 'Опыт работы',  'Требования']].sort_values(by='Зарплата от', ascending=False), hide_index=True, height=300)

with st.expander("Информация об dataframe"):
    st.markdown(f'''
                 Количество найденных вакансий по фильтру {filtered_df.shape[0]}\n
                 Количество вакансий в рублях {filtered_df[filtered_df['Курс валюты'] == 'RUR'].shape[0]}\n
                 Средняя зарплата по нижнией планке {int(filtered_df[filtered_df['Курс валюты'] == 'RUR']['Зарплата от'].dropna().mean())}\n
                 Средняя зарплата по верхней планке {int(filtered_df[filtered_df['Курс валюты'] == 'RUR']['Зарплата до'].dropna().mean())}\n
                 Количество вакансий в долларах {filtered_df[filtered_df['Курс валюты'] == 'USD'].shape[0]}\n
                 ''')
    
st.subheader(f"Тепловая карта с географией компаний вакансий по специальности {specialization} и опытом работы {experience}")

coord = filtered_df[['Latitude', 'Longitude', 'Зарплата от']].dropna().values.tolist()

create_folium_map(geo_data, coord)

st.subheader("Некоторые статистики по всем вакансиям")

col11, col22, col33 = st.columns(3, vertical_alignment='bottom')

with col11:
    get_average_salary_by_profession(df)
with col22:
    get_top_companies_by_salary(df)
with col33:
    get_top_companies_by_count_of_vacancies(df)

st.subheader(f"Наиболее встречающиеся слова в требованиях и обязанностях кандидата на должность {specialization} с опытом работы {experience}")

col111, col222 = st.columns(2)

with col111:
    get_wordcloud_request_company(filtered_df)
with col222:
    get_wordcloud_responsibility_company(filtered_df)

