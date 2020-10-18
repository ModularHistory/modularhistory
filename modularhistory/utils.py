from bs4 import BeautifulSoup


def soupify(value: str) -> BeautifulSoup:
    """
    Wrapper for the BeautifulSoup constructor.

    Specifies `lxml` as the parser.
    """
    return BeautifulSoup(value, features='lxml')
