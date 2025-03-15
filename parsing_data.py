import pandas as pd
import requests
import streamlit as st
import time

def get_vacancies(role, page, date_from, date_to):
    params = {
    "per_page": 100,
    "area": 1,
    "page": page,
    "professional_role": role,
    "date_from": date_from,
    "date_to": date_to
    }

    url = 'https://api.hh.ru/vacancies'
    req = requests.get(url, params=params)
    data = req.json()
    return data

@st.cache_data(show_spinner=False)
def get_list(professional_roles, date_from, date_to):
    lst = []
    seen_ids = set()

    progress_text = "Подождите пожалуйста, пока мы парсим данные с hh.ru"
    my_bar = st.progress(0, text=progress_text)

    for role in professional_roles:
        prog = (professional_roles.index(role) / len(professional_roles)) * 100
        my_bar.progress(int(prog), text=progress_text)

        for page in range(0, 20):
            req_data = get_vacancies(role, page, date_from, date_to)
            for item in req_data.get('items', []):
                vacancy_id = item['id']
                if vacancy_id not in seen_ids:
                    lst.append(item)
                    seen_ids.add(vacancy_id)
    my_bar.empty()
    return lst

def get_df(lst):
    df = pd.DataFrame({'Название вакансии': [v['name'] for v in lst],
                   'Latitude':[v['address']['lat'] if v.get('address') is not None else None for v in lst],
                   'Longitude':[v['address']['lng'] if v.get('address') is not None else None for v in lst],
             'Зарплата от': [v['salary']['from'] if v.get('salary') is not None else None for v in lst],
             'Зарплата до': [v['salary']['to'] if v.get('salary') is not None else None for v in lst],
             'Курс валюты': [v['salary']['currency'] if v.get('salary') is not None else None for v in lst],
             'До вычета налогов': [v['salary']['gross'] if v.get('salary') is not None else None for v in lst],
             'Название компании': [v['employer']['name'] for v in lst],
             'Требования': [v['snippet']['requirement'] for v in lst],
             'Ответственность': [v['snippet']['responsibility'] for v in lst],
             'Профессиональная роль': [v['professional_roles'][0]['name'] for v in lst],
             'Опыт работы': [v['experience']['name'] for v in lst]})
    return df