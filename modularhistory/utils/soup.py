from bs4 import BeautifulSoup


def soupify(html_string: str) -> BeautifulSoup:
    """
    Wrapper for the BeautifulSoup constructor.

    Specifies `lxml` as the parser.
    """
    return BeautifulSoup(html_string, features='lxml')
