"""Tests for HTML parser."""

from app.crawler.parser import HTMLParser


SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
    <meta name="description" content="A test description">
</head>
<body>
    <nav>Navigation menu</nav>
    <header>Site header</header>
    <h1>Main Heading</h1>
    <h2>Sub Heading</h2>
    <p>This is a test paragraph with enough content to be extracted properly by the parser module.</p>
    <ul>
        <li>Item one</li>
        <li>Item two</li>
    </ul>
    <table>
        <tr><th>Col1</th><th>Col2</th></tr>
        <tr><td>A</td><td>B</td></tr>
    </table>
    <a href="/page2">Internal Link</a>
    <a href="https://example.com/doc.pdf">PDF Link</a>
    <img src="/image.png" alt="Test image">
    <div class="ad-banner">Advertisement</div>
    <script>alert('test')</script>
    <footer>Footer content</footer>
</body>
</html>
"""


def test_parse_extracts_title_and_meta():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert result.title == "Test Page"
    assert result.meta_description == "A test description"


def test_parse_extracts_headings():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert "Main Heading" in result.h1
    assert "Sub Heading" in result.h2


def test_parse_extracts_content():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert len(result.paragraphs) >= 1
    assert len(result.lists) >= 1
    assert len(result.tables) >= 1
    assert len(result.images) >= 1
    assert len(result.links) >= 1


def test_parse_extracts_pdfs():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert any("doc.pdf" in pdf for pdf in result.pdfs)


def test_parse_removes_scripts_and_ads():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert "alert" not in result.visible_text
    assert "Advertisement" not in result.visible_text


def test_parse_detects_language():
    parser = HTMLParser()
    result = parser.parse(SAMPLE_HTML, "https://example.com")

    assert result.language == "en"
