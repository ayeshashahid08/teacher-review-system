from datetime import date
def get_current_academic_year() -> str:
    today = date.today()
    month = today.month
    year = today.year
    if month >= 1 and month <= 7:
        return str(year - 1) + "-" + str(year)
    else:
        return str(year) + "-" + str(year + 1)