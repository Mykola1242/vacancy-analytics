# config.py

BASE_URL = "https://www.work.ua"

SEARCH_QUERY = "database+analyst"
MAX_PAGES = 3

SEARCH_URL_TEMPLATE = "https://www.work.ua/jobs-{query}/?page={page}"

RAW_DATA_FILE = "data/vacancies_raw.csv"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


SKILLS_KEYWORDS = [
    "SQL",
    "Python",
    "Excel",
    "Power BI",
    "Tableau",
    "Google Sheets",
    "Pandas",
    "NumPy",
    "ETL",
    "BigQuery",
    "Looker",
    "Power Query",
    "DAX",
    "BI",
    "Data Analysis",
    "Analytics",
    "Oracle",
    "MS SQL",
    "PostgreSQL",
    "MySQL",
]


PROCESSED_DATA_FILE = "output/vacancies_processed.csv"
SKILLS_LONG_FILE = "output/vacancy_skills.csv"


# OLAP analysis output files
OLAP_SUMMARY_FILE = "output/olap_summary.csv"
CITY_ANALYSIS_FILE = "output/city_analysis.csv"
REMOTE_ANALYSIS_FILE = "output/remote_analysis.csv"
SALARY_ANALYSIS_FILE = "output/salary_analysis.csv"
EXPERIENCE_ANALYSIS_FILE = "output/experience_analysis.csv"
EDUCATION_ANALYSIS_FILE = "output/education_analysis.csv"
SKILLS_ANALYSIS_FILE = "output/skills_analysis.csv"



# Visualization output files
VACANCIES_BY_CITY_CHART_FILE = "output/vacancies_by_city.png"
REMOTE_ANALYSIS_CHART_FILE = "output/remote_analysis.png"
SALARY_BY_CITY_CHART_FILE = "output/salary_by_city.png"
TOP_SKILLS_CHART_FILE = "output/top_skills.png"
EXPERIENCE_DISTRIBUTION_CHART_FILE = "output/experience_distribution.png"
EDUCATION_REQUIREMENTS_CHART_FILE = "output/education_requirements.png"