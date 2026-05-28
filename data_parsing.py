# data_parsing.py

import os
import re
import time
from urllib.parse import urljoin

import requests
import pandas as pd
from bs4 import BeautifulSoup

from config import (
    BASE_URL,
    SEARCH_QUERY,
    MAX_PAGES,
    SEARCH_URL_TEMPLATE,
    RAW_DATA_FILE,
    HEADERS,
    SKILLS_KEYWORDS,
)


def build_urls() -> list[str]:
    """
    Формує список URL-адрес сторінок пошуку Work.ua.
    """
    urls = []

    for page in range(1, MAX_PAGES + 1):
        url = SEARCH_URL_TEMPLATE.format(
            query=SEARCH_QUERY,
            page=page
        )
        urls.append(url)

    return urls


def get_html(url: str) -> str:
    """
    Отримує HTML-код однієї сторінки.
    """
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.text


def clean_text(text: str | None) -> str | None:
    """
    Очищує текст від зайвих пробілів та службових символів.
    """
    if text is None:
        return None

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_text_or_none(parent, selector: str) -> str | None:
    """
    Безпечно дістає текст з HTML-елемента.
    Якщо елемент не знайдено — повертає None.
    """
    element = parent.select_one(selector)

    if element is None:
        return None

    return clean_text(element.get_text(" ", strip=True))


def parse_salary(salary_text: str | None) -> dict:
    """
    Парсить зарплату з тексту.

    Приклади:
    '88 000 – 110 000 грн' -> salary_min=88000, salary_max=110000
    '25 000 грн' -> salary_min=25000, salary_max=25000
    None -> salary_min=None, salary_max=None
    """
    if not salary_text:
        return {
            "salary_min": None,
            "salary_max": None,
            "currency": None,
        }

    salary_text = clean_text(salary_text)

    numbers = re.findall(r"\d+", salary_text.replace(" ", ""))

    if not numbers:
        return {
            "salary_min": None,
            "salary_max": None,
            "currency": None,
        }

    numbers = [int(number) for number in numbers]

    if len(numbers) == 1:
        salary_min = numbers[0]
        salary_max = numbers[0]
    else:
        salary_min = numbers[0]
        salary_max = numbers[1]

    currency = "грн" if "грн" in salary_text.lower() else None

    return {
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency,
    }


def extract_employment_type(text: str | None) -> str | None:
    """
    Витягує тип зайнятості з опису вакансії.
    """
    if not text:
        return None

    employment_types = [
        "Повна зайнятість",
        "Неповна зайнятість",
        "Дистанційна робота",
        "Гібридна робота",
    ]

    text_lower = text.lower()

    for employment_type in employment_types:
        if employment_type.lower() in text_lower:
            return employment_type

    return None


def extract_experience(text: str | None) -> str | None:
    """
    Витягує текстову вимогу до досвіду.
    """
    if not text:
        return None

    patterns = [
        r"Досвід роботи[^.]*",
        r"Без досвіду",
        r"від\s+\d+\s+рок",
        r"\d+\s*[-–]\s*\d+\s+рок",
        r"\d+\s+рок",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return clean_text(match.group(0))

    return None


def extract_education(text: str | None) -> str | None:
    """
    Витягує вимогу до освіти.
    """
    if not text:
        return None

    text_lower = text.lower()

    if "незакінчена вища" in text_lower:
        return "Незакінчена вища освіта"

    if "вища освіта" in text_lower:
        return "Вища освіта"

    if "середня спеціальна" in text_lower:
        return "Середня спеціальна освіта"

    if "середня освіта" in text_lower:
        return "Середня освіта"

    return None


def extract_skills(text: str | None) -> str | None:
    """
    Шукає ключові навички у тексті вакансії.
    """
    if not text:
        return None

    found_skills = []
    text_lower = text.lower()

    for skill in SKILLS_KEYWORDS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    if not found_skills:
        return None

    return ", ".join(sorted(set(found_skills)))


def extract_salary_text(card) -> str | None:
    """
    Шукає зарплату в картці вакансії.

    У Work.ua зарплата також має клас strong-600,
    але компанія теж може мати strong-600.
    Тому перевіряємо, чи є в тексті 'грн'.
    """
    strong_elements = card.select("span.strong-600")

    for element in strong_elements:
        text = clean_text(element.get_text(" ", strip=True))

        if text and "грн" in text.lower():
            return text

    return None


def extract_company(card) -> str | None:
    """
    Витягує назву компанії.

    У картці Work.ua компанія зазвичай лежить у блоці div.mt-xs
    всередині span.mr-xs span.strong-600.
    """
    return get_text_or_none(card, "div.mt-xs span.mr-xs span.strong-600")


def extract_location(card) -> str | None:
    """
    Витягує місто або дистанційний формат.
    """
    info_block = card.select_one("div.mt-xs")

    if info_block is None:
        return None

    direct_spans = info_block.find_all("span", recursive=False)

    for span in direct_spans:
        text = clean_text(span.get_text(" ", strip=True))

        if not text:
            continue

        if text == extract_company(card):
            continue

        return text

    return None


def parse_vacancy_card(card, page_number: int) -> dict:
    """
    Парсить одну картку вакансії.
    """
    title_tag = card.select_one("h2 a")

    title = clean_text(title_tag.get_text(" ", strip=True)) if title_tag else None

    href = title_tag.get("href") if title_tag else None
    vacancy_url = urljoin(BASE_URL, href) if href else None

    company = extract_company(card)
    location = extract_location(card)

    salary_text = extract_salary_text(card)
    salary_data = parse_salary(salary_text)

    description = get_text_or_none(card, "p.ellipsis")

    employment_type = extract_employment_type(description)
    experience = extract_experience(description)
    education = extract_education(description)

    skills_source = f"{title or ''} {description or ''}"
    skills = extract_skills(skills_source)

    date_tag = card.select_one("time")
    date_text = clean_text(date_tag.get_text(" ", strip=True)) if date_tag else None
    date_datetime = date_tag.get("datetime") if date_tag else None

    return {
        "title": title,
        "company": company,
        "location": location,
        "salary_text": salary_text,
        "salary_min": salary_data["salary_min"],
        "salary_max": salary_data["salary_max"],
        "currency": salary_data["currency"],
        "employment_type": employment_type,
        "experience": experience,
        "education": education,
        "skills": skills,
        "description": description,
        "date_text": date_text,
        "date_datetime": date_datetime,
        "url": vacancy_url,
        "source": "Work.ua",
        "page": page_number,
    }


def parse_search_page(html: str, page_number: int) -> list[dict]:
    """
    Парсить одну сторінку пошуку вакансій.
    """
    soup = BeautifulSoup(html, "lxml")

    cards = soup.select("div.card.card-hover.card-visited.wordwrap.job-link")

    vacancies = []

    for card in cards:
        vacancy = parse_vacancy_card(card, page_number)

        if vacancy["title"] and vacancy["url"]:
            vacancies.append(vacancy)

    return vacancies


def scrape_vacancies() -> pd.DataFrame:
    """
    Парсить усі сторінки пошуку та повертає DataFrame.
    """
    urls = build_urls()
    all_vacancies = []

    for page_number, url in enumerate(urls, start=1):
        print(f"Парсинг сторінки {page_number}: {url}")

        html = get_html(url)
        vacancies = parse_search_page(html, page_number)

        print(f"Знайдено вакансій: {len(vacancies)}")

        all_vacancies.extend(vacancies)

        time.sleep(1)

    dataframe = pd.DataFrame(all_vacancies)

    if not dataframe.empty:
        dataframe.drop_duplicates(subset=["url"], inplace=True)

    return dataframe


def save_raw_data(dataframe: pd.DataFrame, file_path: str) -> None:
    """
    Зберігає сирі спарсені дані у CSV.
    """
    output_directory = os.path.dirname(file_path)

    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)

    dataframe.to_csv(file_path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    vacancies_df = scrape_vacancies()

    print()
    print("Перші рядки таблиці:")
    print(vacancies_df.head())

    print()
    print(f"Усього вакансій: {len(vacancies_df)}")

    save_raw_data(vacancies_df, RAW_DATA_FILE)

    print()
    print("Дані збережено у файл:")
    print(RAW_DATA_FILE)