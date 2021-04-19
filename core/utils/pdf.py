"""Utils module for working with PDF files, URLs, etc."""

PAGE_KEY = 'page'


def url_specifies_page(url: str) -> bool:
    """Return True if the PDF url specifies the page number to open, else False."""
    if f'#{PAGE_KEY}=' in url:
        return True
    return False
