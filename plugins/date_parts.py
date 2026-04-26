import datetime


def get_current_date_parts():
    """Get current date for partitioning in s3"""
    now = datetime.datetime.now()
    return {
        'year': now.year,
        'month': now.month,
        'day': now.day
    }
