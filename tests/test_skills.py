from src.skills import extract_skills

def test_extract_basic():
    text = "We use Python, SQL and Airflow on AWS."
    found = extract_skills(text)
    assert "python" in found
    assert "sql" in found
    assert "airflow" in found
