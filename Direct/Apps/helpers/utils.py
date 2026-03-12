from datetime import datetime
            
def normalize_date(date_str):
    """Normalizes a date string to a standard format."""
    date_formats = [
        "%m/%d/%Y", "%m/%d/%y",                
        "%m-%d-%Y", "%m-%d-%y",
        "%b %d, %Y", "%B %d, %Y",  # Jan 2, 2024 / January 2, 2024
        "%b %d, %y", "%B %d, %y",
        "%Y-%m-%d",
    ]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # return dt.strftime("%Y-%m-%d")
            return dt
        except ValueError:
            continue
    return date_str