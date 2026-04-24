import datetime


def get_date():
    """Get current date for partitioning in s3"""
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return year, month, day
