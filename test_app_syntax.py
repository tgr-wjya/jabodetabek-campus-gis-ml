# test_app_syntax.py
import py_compile
import unittest

class TestAppSyntax(unittest.TestCase):
    def test_app_py_compiles(self):
        py_compile.compile("app.py", doraise=True)

    def test_required_libraries_installed(self):
        import streamlit
        import folium
        import pandas
        import sklearn
        import altair

if __name__ == "__main__":
    unittest.main()
