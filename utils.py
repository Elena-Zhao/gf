import datetime as dt
from re import sub

def parse_currency(string):
    """Preprocess string and get currency number
          
    >>> parse_currency('$2,000')
    2000.0
    """
    return float(sub(r'[^\d.]', '', string))


def parse_date(string):
    """Get datetime

    >>> parse_date('08/22/2017')
    datetime.datetime(2017, 8, 22, 0, 0)
    """
    if string == 'Pending':
        date = dt.datetime(9999,1,1)
    else:
        try:
            date = dt.datetime.strptime(string, '%m/%d/%Y')
        except:
            print("Error in parse_date(%s)" % (string))
            date = dt.datetime(1999,1,1)
    return date


if __name__ == "__main__":
    import doctest
    doctest.testmod()
