# olap_analysis.py

import os

import pandas as pd

from config import (
    PROCESSED_DATA_FILE,
    SKILLS_LONG_FILE,
    OLAP_SUMMARY_FILE,
    CITY_ANALYSIS_FILE,
    REMOTE_ANALYSIS_FILE,
    SALARY_ANALYSIS_FILE,
    EXPERIENCE_ANALYSIS_FILE,
    EDUCATION_ANALYSIS_FILE,
    SKILLS_ANALYSIS_FILE,
)


def create_output_directory(file_path: str) -> None:
    """
    Створює папку для збереження файлу, якщо її ще не існує.
    """
    output_directory = os.path.dirname(file_path)

    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)


def save_dataframe(df: pd.DataFrame, file_path: str) -> None:
    """
    Зберігає DataFrame у CSV-файл.
    """
    create_output_directory(file_path)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")


def build_olap_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує загальне OLAP-зведення по вакансіях.
    """
    total_vacancies = len(df)
    salary_available_count = int(df["salary_available"].sum())
    salary_missing_count = total_vacancies - salary_available_count

    remote_count = int(df["is_remote"].sum())
    office_count = total_vacancies - remote_count

    avg_salary = df["salary_avg"].mean()
    min_salary = df["salary_min"].min()
    max_salary = df["salary_max"].max()

    summary = [
        {
            "indicator": "Кількість вакансій",
            "value": total_vacancies,
        },
        {
            "indicator": "Кількість вакансій із зарплатою",
            "value": salary_available_count,
        },
        {
            "indicator": "Кількість вакансій без зарплати",
            "value": salary_missing_count,
        },
        {
            "indicator": "Кількість дистанційних вакансій",
            "value": remote_count,
        },
        {
            "indicator": "Кількість офісних / локальних вакансій",
            "value": office_count,
        },
        {
            "indicator": "Середня зарплата",
            "value": round(avg_salary, 2) if pd.notna(avg_salary) else None,
        },
        {
            "indicator": "Мінімальна зарплата",
            "value": round(min_salary, 2) if pd.notna(min_salary) else None,
        },
        {
            "indicator": "Максимальна зарплата",
            "value": round(max_salary, 2) if pd.notna(max_salary) else None,
        },
        {
            "indicator": "Кількість міст / локацій",
            "value": df["city"].nunique(),
        },
    ]

    return pd.DataFrame(summary)


def build_city_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує OLAP-зріз кількості вакансій за містами.
    """
    city_df = (
        df.groupby("city")
        .agg(
            vacancies_count=("title", "count"),
            salary_available_count=("salary_available", "sum"),
            average_salary=("salary_avg", "mean"),
            average_skills_count=("skills_count", "mean"),
        )
        .reset_index()
    )

    city_df["average_salary"] = city_df["average_salary"].round(2)
    city_df["average_skills_count"] = city_df["average_skills_count"].round(2)

    city_df = city_df.sort_values(
        by="vacancies_count",
        ascending=False
    ).reset_index(drop=True)

    return city_df


def build_remote_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує OLAP-зріз за форматом роботи: дистанційно / не дистанційно.
    """
    remote_df = (
        df.groupby("is_remote")
        .agg(
            vacancies_count=("title", "count"),
            salary_available_count=("salary_available", "sum"),
            average_salary=("salary_avg", "mean"),
            average_skills_count=("skills_count", "mean"),
        )
        .reset_index()
    )

    remote_df["work_format"] = remote_df["is_remote"].map(
        {
            True: "Дистанційно",
            False: "Офіс / місто",
        }
    )

    remote_df["average_salary"] = remote_df["average_salary"].round(2)
    remote_df["average_skills_count"] = remote_df["average_skills_count"].round(2)

    remote_df = remote_df[
        [
            "work_format",
            "vacancies_count",
            "salary_available_count",
            "average_salary",
            "average_skills_count",
        ]
    ]

    return remote_df


def build_salary_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує зарплатний OLAP-аналіз за містами.
    Враховуються тільки вакансії, де зарплата вказана.
    """
    salary_df = df[df["salary_available"] == True].copy()

    if salary_df.empty:
        return pd.DataFrame(
            columns=[
                "city",
                "vacancies_with_salary",
                "min_salary",
                "max_salary",
                "average_salary",
            ]
        )

    salary_analysis = (
        salary_df.groupby("city")
        .agg(
            vacancies_with_salary=("title", "count"),
            min_salary=("salary_min", "min"),
            max_salary=("salary_max", "max"),
            average_salary=("salary_avg", "mean"),
        )
        .reset_index()
    )

    salary_analysis["average_salary"] = salary_analysis["average_salary"].round(2)

    salary_analysis = salary_analysis.sort_values(
        by="average_salary",
        ascending=False
    ).reset_index(drop=True)

    return salary_analysis


def build_experience_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує OLAP-зріз вакансій за категоріями досвіду.
    """
    experience_df = (
        df.groupby("experience_category")
        .agg(
            vacancies_count=("title", "count"),
            average_salary=("salary_avg", "mean"),
            average_skills_count=("skills_count", "mean"),
        )
        .reset_index()
    )

    experience_df["average_salary"] = experience_df["average_salary"].round(2)
    experience_df["average_skills_count"] = experience_df[
        "average_skills_count"
    ].round(2)

    experience_df = experience_df.sort_values(
        by="vacancies_count",
        ascending=False
    ).reset_index(drop=True)

    return experience_df


def build_education_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує OLAP-зріз за вимогами до освіти.
    """
    temp_df = df.copy()

    temp_df["education_group"] = temp_df["education"].fillna("Не вказано")

    education_df = (
        temp_df.groupby("education_group")
        .agg(
            vacancies_count=("title", "count"),
            average_salary=("salary_avg", "mean"),
            average_skills_count=("skills_count", "mean"),
        )
        .reset_index()
    )

    education_df["average_salary"] = education_df["average_salary"].round(2)
    education_df["average_skills_count"] = education_df[
        "average_skills_count"
    ].round(2)

    education_df = education_df.sort_values(
        by="vacancies_count",
        ascending=False
    ).reset_index(drop=True)

    return education_df


def build_skills_analysis(skills_df: pd.DataFrame) -> pd.DataFrame:
    """
    Формує OLAP-зріз за навичками.
    """
    if skills_df.empty:
        return pd.DataFrame(
            columns=[
                "skill",
                "mentions_count",
                "unique_vacancies_count",
            ]
        )

    skills_analysis = (
        skills_df.groupby("skill")
        .agg(
            mentions_count=("skill", "count"),
            unique_vacancies_count=("url", "nunique"),
        )
        .reset_index()
    )

    skills_analysis = skills_analysis.sort_values(
        by="mentions_count",
        ascending=False
    ).reset_index(drop=True)

    return skills_analysis


def run_olap_analysis(
    processed_df: pd.DataFrame,
    skills_df: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """
    Запускає всі OLAP-зрізи та повертає словник таблиць.
    """
    olap_tables = {
        "summary": build_olap_summary(processed_df),
        "city_analysis": build_city_analysis(processed_df),
        "remote_analysis": build_remote_analysis(processed_df),
        "salary_analysis": build_salary_analysis(processed_df),
        "experience_analysis": build_experience_analysis(processed_df),
        "education_analysis": build_education_analysis(processed_df),
        "skills_analysis": build_skills_analysis(skills_df),
    }

    return olap_tables


if __name__ == "__main__":
    processed_df = pd.read_csv(PROCESSED_DATA_FILE)

    try:
        skills_df = pd.read_csv(SKILLS_LONG_FILE)
    except FileNotFoundError:
        skills_df = pd.DataFrame(
            columns=[
                "title",
                "company",
                "city",
                "url",
                "skill",
            ]
        )

    olap_tables = run_olap_analysis(processed_df, skills_df)

    save_dataframe(olap_tables["summary"], OLAP_SUMMARY_FILE)
    save_dataframe(olap_tables["city_analysis"], CITY_ANALYSIS_FILE)
    save_dataframe(olap_tables["remote_analysis"], REMOTE_ANALYSIS_FILE)
    save_dataframe(olap_tables["salary_analysis"], SALARY_ANALYSIS_FILE)
    save_dataframe(olap_tables["experience_analysis"], EXPERIENCE_ANALYSIS_FILE)
    save_dataframe(olap_tables["education_analysis"], EDUCATION_ANALYSIS_FILE)
    save_dataframe(olap_tables["skills_analysis"], SKILLS_ANALYSIS_FILE)

    print("OLAP-аналіз завершено.")
    print()
    print("Загальне зведення:")
    print("-" * 80)
    print(olap_tables["summary"].to_string(index=False))

    print()
    print("Вакансії за містами:")
    print("-" * 80)
    print(olap_tables["city_analysis"].to_string(index=False))

    print()
    print("Топ навичок:")
    print("-" * 80)
    print(olap_tables["skills_analysis"].head(15).to_string(index=False))

    print()
    print("Файли збережено:")
    print(OLAP_SUMMARY_FILE)
    print(CITY_ANALYSIS_FILE)
    print(REMOTE_ANALYSIS_FILE)
    print(SALARY_ANALYSIS_FILE)
    print(EXPERIENCE_ANALYSIS_FILE)
    print(EDUCATION_ANALYSIS_FILE)
    print(SKILLS_ANALYSIS_FILE)