import pytest
from unittest.mock import patch, Mock
from downloader.core import obter_soup, extrair_links_anexos

@patch("downloader.core.requests.get")
def test_obter_soup(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><a href='anexo1.pdf'>anexo I</a></body></html>"
    mock_get.return_value = mock_response

    soup = obter_soup("http://exemplo.com")
    assert soup is not None
    assert soup.find("a").text.lower() == "anexo i"

def test_extrair_links_anexos():
    from bs4 import BeautifulSoup
    html = "<html><body><a href='http://site.com/anexo1.pdf'>anexo I</a></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    anexos = extrair_links_anexos(soup)
    assert len(anexos) == 1
    assert anexos[0][0] == "anexo1.pdf"
