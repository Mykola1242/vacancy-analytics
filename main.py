# main.py

import pandas as pd

from config import (
    RAW_DATA_FILE,
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

from data_parsing import scrape_vacancies, save_raw_data
from data_processing import (
    process_vacancies,
    create_skills_long_table,
    save_dataframe as save_processed_dataframe,
)
from olap_analysis import (
    run_olap_analysis,
    save_dataframe as save_olap_dataframe,
)
from visualization import build_all_visualizations


def show_menu() -> None:
    """
    Виводить головне меню програми.
    """
    print()
    print("=" * 80)
    print("Лабораторна робота №4")
    print("Завдання 2: аналіз вакансій Data Analyst з Work.ua")
    print("Парсинг + Data Processing + OLAP + Visualization")
    print("=" * 80)
    print("1. Запустити повний процес")
    print("2. Тільки парсинг вакансій")
    print("3. Тільки обробка даних")
    print("4. Тільки OLAP-аналіз")
    print("5. Тільки побудова графіків")
    print("0. Вийти")
    print("=" * 80)


def run_parsing() -> None:
    """
    Запускає парсинг вакансій з Work.ua.
    """
    print()
    print("Запуск парсингу вакансій...")

    vacancies_df = scrape_vacancies()
    save_raw_data(vacancies_df, RAW_DATA_FILE)

    print()
    print("Парсинг завершено.")
    print(f"Кількість зібраних вакансій: {len(vacancies_df)}")
    print(f"Файл збережено: {RAW_DATA_FILE}")


def run_processing() -> None:
    """
    Запускає обробку сирих даних.
    """
    print()
    print("Запуск обробки даних...")

    raw_df = pd.read_csv(RAW_DATA_FILE)

    processed_df = process_vacancies(raw_df)
    skills_long_df = create_skills_long_table(processed_df)

    save_processed_dataframe(processed_df, PROCESSED_DATA_FILE)
    save_processed_dataframe(skills_long_df, SKILLS_LONG_FILE)

    print()
    print("Обробка даних завершена.")
    print(f"Оброблених вакансій: {len(processed_df)}")
    print(f"Записів навичок: {len(skills_long_df)}")
    print(f"Файл з обробленими вакансіями: {PROCESSED_DATA_FILE}")
    print(f"Файл з навичками: {SKILLS_LONG_FILE}")


def run_olap() -> None:
    """
    Запускає OLAP-аналіз оброблених даних.
    """
    print()
    print("Запуск OLAP-аналізу...")

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

    save_olap_dataframe(olap_tables["summary"], OLAP_SUMMARY_FILE)
    save_olap_dataframe(olap_tables["city_analysis"], CITY_ANALYSIS_FILE)
    save_olap_dataframe(olap_tables["remote_analysis"], REMOTE_ANALYSIS_FILE)
    save_olap_dataframe(olap_tables["salary_analysis"], SALARY_ANALYSIS_FILE)
    save_olap_dataframe(olap_tables["experience_analysis"], EXPERIENCE_ANALYSIS_FILE)
    save_olap_dataframe(olap_tables["education_analysis"], EDUCATION_ANALYSIS_FILE)
    save_olap_dataframe(olap_tables["skills_analysis"], SKILLS_ANALYSIS_FILE)

    print()
    print("OLAP-аналіз завершено.")
    print()
    print("Загальне зведення:")
    print("-" * 80)
    print(olap_tables["summary"].to_string(index=False))

    print()
    print("Топ навичок:")
    print("-" * 80)
    print(olap_tables["skills_analysis"].head(10).to_string(index=False))


def run_visualization() -> None:
    """
    Запускає побудову всіх графіків.
    """
    print()
    print("Побудова OLAP-графіків...")

    build_all_visualizations(show=True)

    print()
    print("Графіки успішно побудовано та збережено в папку output.")


def run_full_pipeline() -> None:
    """
    Запускає повний процес:
    1. Парсинг.
    2. Обробка даних.
    3. OLAP-аналіз.
    4. Побудова графіків.
    """
    run_parsing()
    run_processing()
    run_olap()
    run_visualization()

    print()
    print("=" * 80)
    print("Повний процес виконано успішно.")
    print("=" * 80)


def main() -> None:
    """
    Головна функція програми.
    """
    while True:
        show_menu()

        choice = input("Оберіть пункт меню: ").strip()

        if choice == "1":
            try:
                run_full_pipeline()
            except Exception as error:
                print()
                print(f"Помилка під час виконання повного процесу: {error}")

        elif choice == "2":
            try:
                run_parsing()
            except Exception as error:
                print()
                print(f"Помилка під час парсингу: {error}")

        elif choice == "3":
            try:
                run_processing()
            except Exception as error:
                print()
                print(f"Помилка під час обробки даних: {error}")

        elif choice == "4":
            try:
                run_olap()
            except Exception as error:
                print()
                print(f"Помилка під час OLAP-аналізу: {error}")

        elif choice == "5":
            try:
                run_visualization()
            except Exception as error:
                print()
                print(f"Помилка під час побудови графіків: {error}")

        elif choice == "0":
            print()
            print("Роботу програми завершено.")
            break

        else:
            print()
            print("Некоректний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()