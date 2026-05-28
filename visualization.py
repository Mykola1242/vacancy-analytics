# visualization.py

import os

import pandas as pd
import matplotlib.pyplot as plt

from config import (
    CITY_ANALYSIS_FILE,
    REMOTE_ANALYSIS_FILE,
    SALARY_ANALYSIS_FILE,
    EXPERIENCE_ANALYSIS_FILE,
    EDUCATION_ANALYSIS_FILE,
    SKILLS_ANALYSIS_FILE,
    VACANCIES_BY_CITY_CHART_FILE,
    REMOTE_ANALYSIS_CHART_FILE,
    SALARY_BY_CITY_CHART_FILE,
    TOP_SKILLS_CHART_FILE,
    EXPERIENCE_DISTRIBUTION_CHART_FILE,
    EDUCATION_REQUIREMENTS_CHART_FILE,
)


def create_output_directory(file_path: str) -> None:
    """
    Створює папку для збереження графіка, якщо її ще не існує.
    """
    output_directory = os.path.dirname(file_path)

    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)


def plot_vacancies_by_city(
    city_df: pd.DataFrame,
    output_path: str,
    show: bool = False,
    top_n: int = 10
) -> None:
    """
    Будує графік кількості вакансій за містами.
    """
    create_output_directory(output_path)

    plot_df = city_df.sort_values(
        by="vacancies_count",
        ascending=True
    ).tail(top_n)

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_df["city"],
        plot_df["vacancies_count"]
    )

    plt.xlabel("Кількість вакансій")
    plt.ylabel("Місто / локація")
    plt.title("Кількість вакансій за містами")

    for index, value in enumerate(plot_df["vacancies_count"]):
        plt.text(
            value + 0.1,
            index,
            str(value),
            va="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_remote_distribution(
    remote_df: pd.DataFrame,
    output_path: str,
    show: bool = False
) -> None:
    """
    Будує графік розподілу вакансій за форматом роботи:
    дистанційно / офіс або місто.
    """
    create_output_directory(output_path)

    plt.figure(figsize=(8, 5))

    plt.bar(
        remote_df["work_format"],
        remote_df["vacancies_count"]
    )

    plt.xlabel("Формат роботи")
    plt.ylabel("Кількість вакансій")
    plt.title("Розподіл вакансій за форматом роботи")

    for index, value in enumerate(remote_df["vacancies_count"]):
        plt.text(
            index,
            value + 0.1,
            str(value),
            ha="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_salary_by_city(
    salary_df: pd.DataFrame,
    output_path: str,
    show: bool = False,
    top_n: int = 10
) -> None:
    """
    Будує графік середньої зарплати за містами.
    Враховуються тільки вакансії, де зарплата була вказана.
    """
    create_output_directory(output_path)

    if salary_df.empty:
        print("Немає даних для побудови графіка зарплат.")
        return

    plot_df = salary_df.sort_values(
        by="average_salary",
        ascending=True
    ).tail(top_n)

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_df["city"],
        plot_df["average_salary"]
    )

    plt.xlabel("Середня зарплата, грн")
    plt.ylabel("Місто / локація")
    plt.title("Середня зарплата за містами")

    for index, value in enumerate(plot_df["average_salary"]):
        plt.text(
            value + 500,
            index,
            f"{value:.0f}",
            va="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_top_skills(
    skills_df: pd.DataFrame,
    output_path: str,
    show: bool = False,
    top_n: int = 10
) -> None:
    """
    Будує графік найчастіше згаданих навичок.
    """
    create_output_directory(output_path)

    if skills_df.empty:
        print("Немає даних для побудови графіка навичок.")
        return

    plot_df = skills_df.sort_values(
        by="mentions_count",
        ascending=True
    ).tail(top_n)

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_df["skill"],
        plot_df["mentions_count"]
    )

    plt.xlabel("Кількість згадувань")
    plt.ylabel("Навичка")
    plt.title("ТОП навичок у вакансіях Data Analyst")

    for index, value in enumerate(plot_df["mentions_count"]):
        plt.text(
            value + 0.1,
            index,
            str(value),
            va="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_experience_distribution(
    experience_df: pd.DataFrame,
    output_path: str,
    show: bool = False
) -> None:
    """
    Будує графік розподілу вакансій за вимогами до досвіду.
    """
    create_output_directory(output_path)

    plot_df = experience_df.sort_values(
        by="vacancies_count",
        ascending=True
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_df["experience_category"],
        plot_df["vacancies_count"]
    )

    plt.xlabel("Кількість вакансій")
    plt.ylabel("Категорія досвіду")
    plt.title("Розподіл вакансій за вимогами до досвіду")

    for index, value in enumerate(plot_df["vacancies_count"]):
        plt.text(
            value + 0.1,
            index,
            str(value),
            va="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_education_requirements(
    education_df: pd.DataFrame,
    output_path: str,
    show: bool = False
) -> None:
    """
    Будує графік розподілу вакансій за вимогами до освіти.
    """
    create_output_directory(output_path)

    plot_df = education_df.sort_values(
        by="vacancies_count",
        ascending=True
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_df["education_group"],
        plot_df["vacancies_count"]
    )

    plt.xlabel("Кількість вакансій")
    plt.ylabel("Освіта")
    plt.title("Розподіл вакансій за вимогами до освіти")

    for index, value in enumerate(plot_df["vacancies_count"]):
        plt.text(
            value + 0.1,
            index,
            str(value),
            va="center"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    if show:
        plt.show()

    plt.close()


def build_all_visualizations(show: bool = False) -> None:
    """
    Завантажує OLAP-таблиці та будує всі графіки.
    """
    city_df = pd.read_csv(CITY_ANALYSIS_FILE)
    remote_df = pd.read_csv(REMOTE_ANALYSIS_FILE)
    salary_df = pd.read_csv(SALARY_ANALYSIS_FILE)
    experience_df = pd.read_csv(EXPERIENCE_ANALYSIS_FILE)
    education_df = pd.read_csv(EDUCATION_ANALYSIS_FILE)
    skills_df = pd.read_csv(SKILLS_ANALYSIS_FILE)

    plot_vacancies_by_city(
        city_df,
        VACANCIES_BY_CITY_CHART_FILE,
        show=show
    )

    plot_remote_distribution(
        remote_df,
        REMOTE_ANALYSIS_CHART_FILE,
        show=show
    )

    plot_salary_by_city(
        salary_df,
        SALARY_BY_CITY_CHART_FILE,
        show=show
    )

    plot_top_skills(
        skills_df,
        TOP_SKILLS_CHART_FILE,
        show=show
    )

    plot_experience_distribution(
        experience_df,
        EXPERIENCE_DISTRIBUTION_CHART_FILE,
        show=show
    )

    plot_education_requirements(
        education_df,
        EDUCATION_REQUIREMENTS_CHART_FILE,
        show=show
    )


if __name__ == "__main__":
    build_all_visualizations(show=True)

    print("OLAP-візуалізацію завершено.")
    print()
    print("Графіки збережено:")
    print(VACANCIES_BY_CITY_CHART_FILE)
    print(REMOTE_ANALYSIS_CHART_FILE)
    print(SALARY_BY_CITY_CHART_FILE)
    print(TOP_SKILLS_CHART_FILE)
    print(EXPERIENCE_DISTRIBUTION_CHART_FILE)
    print(EDUCATION_REQUIREMENTS_CHART_FILE)