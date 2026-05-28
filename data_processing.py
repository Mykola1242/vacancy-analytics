# data_processing.py

import os
import re

import pandas as pd

from config import (
    RAW_DATA_FILE,
    PROCESSED_DATA_FILE,
    SKILLS_LONG_FILE,
)


def create_output_directory(file_path: str) -> None:
    """
    Створює папку для збереження файлу, якщо її ще не існує.
    """
    output_directory = os.path.dirname(file_path)

    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)


def clean_text(value) -> str | None:
    """
    Очищує текстове значення.
    """
    if pd.isna(value):
        return None

    text = str(value)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_location(location: str | None) -> dict:
    """
    Нормалізує локацію вакансії.

    Приклади:
    'Дистанційно' -> city='Дистанційно', is_remote=True
    'Київ, 3,1 км від центру' -> city='Київ', is_remote=False
    'Городок (Львівська обл.), шукаємо у Львові' -> city='Городок (Львівська обл.)'
    """
    location = clean_text(location)

    if not location:
        return {
            "city": "Не вказано",
            "is_remote": False,
        }

    location_lower = location.lower()

    if "дистанційно" in location_lower:
        return {
            "city": "Дистанційно",
            "is_remote": True,
        }

    city = location.split(",")[0].strip()

    return {
        "city": city,
        "is_remote": False,
    }


def calculate_salary_avg(row) -> float | None:
    """
    Обчислює середню зарплату на основі salary_min та salary_max.
    """
    salary_min = row.get("salary_min")
    salary_max = row.get("salary_max")

    if pd.isna(salary_min) or pd.isna(salary_max):
        return None

    return round((float(salary_min) + float(salary_max)) / 2, 2)


def parse_experience_years(experience_text: str | None) -> dict:
    """
    Перетворює текст досвіду у числові значення.

    Приклади:
    'Досвід роботи від 2 років' -> min=2, max=None
    'Досвід роботи 3-5 років' -> min=3, max=5
    'Без досвіду' -> min=0, max=0
    """
    experience_text = clean_text(experience_text)

    if not experience_text:
        return {
            "experience_min": None,
            "experience_max": None,
            "experience_category": "Не вказано",
        }

    text = experience_text.lower().replace("–", "-")

    if "без досвіду" in text:
        return {
            "experience_min": 0,
            "experience_max": 0,
            "experience_category": "Без досвіду",
        }

    range_match = re.search(r"(\d+)\s*-\s*(\d+)", text)

    if range_match:
        min_years = int(range_match.group(1))
        max_years = int(range_match.group(2))

        return {
            "experience_min": min_years,
            "experience_max": max_years,
            "experience_category": f"{min_years}-{max_years} років",
        }

    from_match = re.search(r"від\s+(\d+)", text)

    if from_match:
        min_years = int(from_match.group(1))

        return {
            "experience_min": min_years,
            "experience_max": None,
            "experience_category": f"Від {min_years} років",
        }

    single_match = re.search(r"(\d+)\s+рок", text)

    if single_match:
        years = int(single_match.group(1))

        return {
            "experience_min": years,
            "experience_max": years,
            "experience_category": f"{years} років",
        }

    return {
        "experience_min": None,
        "experience_max": None,
        "experience_category": "Не вказано",
    }


def calculate_skills_count(skills: str | None) -> int:
    """
    Рахує кількість знайдених навичок у вакансії.
    """
    skills = clean_text(skills)

    if not skills:
        return 0

    return len([skill.strip() for skill in skills.split(",") if skill.strip()])


def create_skills_long_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Створює окрему таблицю навичок.

    Було:
    title | skills
    Data Analyst | SQL, Python, Power BI

    Стає:
    title | skill
    Data Analyst | SQL
    Data Analyst | Python
    Data Analyst | Power BI
    """
    rows = []

    for _, row in df.iterrows():
        skills = clean_text(row.get("skills"))

        if not skills:
            continue

        for skill in skills.split(","):
            skill = skill.strip()

            if not skill:
                continue

            rows.append(
                {
                    "title": row.get("title"),
                    "company": row.get("company"),
                    "city": row.get("city"),
                    "url": row.get("url"),
                    "skill": skill,
                }
            )

    return pd.DataFrame(rows)


def process_vacancies(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Основна функція обробки вакансій.
    """
    df = raw_df.copy()

    text_columns = [
        "title",
        "company",
        "location",
        "salary_text",
        "currency",
        "employment_type",
        "experience",
        "education",
        "skills",
        "description",
        "date_text",
        "url",
        "source",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].apply(clean_text)

    location_data = df["location"].apply(normalize_location)
    df["city"] = location_data.apply(lambda item: item["city"])
    df["is_remote"] = location_data.apply(lambda item: item["is_remote"])

    df["salary_available"] = df["salary_min"].notna() & df["salary_max"].notna()
    df["salary_avg"] = df.apply(calculate_salary_avg, axis=1)

    experience_data = df["experience"].apply(parse_experience_years)
    df["experience_min"] = experience_data.apply(lambda item: item["experience_min"])
    df["experience_max"] = experience_data.apply(lambda item: item["experience_max"])
    df["experience_category"] = experience_data.apply(
        lambda item: item["experience_category"]
    )

    df["education_required"] = df["education"].notna()
    df["skills_count"] = df["skills"].apply(calculate_skills_count)

    # Зручний порядок колонок
    columns_order = [
        "title",
        "company",
        "city",
        "location",
        "is_remote",
        "salary_text",
        "salary_min",
        "salary_max",
        "salary_avg",
        "currency",
        "salary_available",
        "employment_type",
        "experience",
        "experience_min",
        "experience_max",
        "experience_category",
        "education",
        "education_required",
        "skills",
        "skills_count",
        "description",
        "date_text",
        "date_datetime",
        "url",
        "source",
        "page",
    ]

    existing_columns = [
        column for column in columns_order
        if column in df.columns
    ]

    df = df[existing_columns]

    return df


def save_dataframe(df: pd.DataFrame, file_path: str) -> None:
    """
    Зберігає DataFrame у CSV.
    """
    create_output_directory(file_path)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    raw_df = pd.read_csv(RAW_DATA_FILE)

    processed_df = process_vacancies(raw_df)
    skills_long_df = create_skills_long_table(processed_df)

    save_dataframe(processed_df, PROCESSED_DATA_FILE)
    save_dataframe(skills_long_df, SKILLS_LONG_FILE)

    print("Обробка даних завершена.")
    print()
    print(f"Вхідних вакансій: {len(raw_df)}")
    print(f"Оброблених вакансій: {len(processed_df)}")
    print(f"Знайдено записів навичок: {len(skills_long_df)}")
    print()
    print("Файли збережено:")
    print(PROCESSED_DATA_FILE)
    print(SKILLS_LONG_FILE)

    print()
    print("Перші рядки обробленої таблиці:")
    print(processed_df.head())