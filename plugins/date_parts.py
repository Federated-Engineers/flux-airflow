import datetime


def get_current_date_parts():
    """Get current date for partitioning in s3"""
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return year, month, day
