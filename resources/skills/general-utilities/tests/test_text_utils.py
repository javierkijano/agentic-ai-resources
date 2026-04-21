import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core/logic')))
import text_utils

def test_sanitize_filename():
    assert text_utils.sanitize_filename("invalid:file*name.txt") == "invalid_file_name.txt"
    assert text_utils.sanitize_filename("valid_file-name.txt") == "valid_file-name.txt"

def test_extract_urls():
    text = "Check out https://google.com and http://example.org/test"
    urls = text_utils.extract_urls(text)
    assert urls == ["https://google.com", "http://example.org"]

def test_truncate_text():
    assert text_utils.truncate_text("Short text") == "Short text"
    assert text_utils.truncate_text("This is a very long text indeed", 15) == "This is a ve..."

if __name__ == '__main__':
    test_sanitize_filename()
    test_extract_urls()
    test_truncate_text()
    print("All text_utils tests passed!")
