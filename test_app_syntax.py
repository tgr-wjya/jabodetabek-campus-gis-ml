# test_app_syntax.py
import py_compile
import unittest


class TestAppSyntax(unittest.TestCase):
    def test_app_py_compiles(self):
        py_compile.compile("app.py", doraise=True)

    def test_required_libraries_installed(self):
        import altair  # noqa: F401
        import folium  # noqa: F401
        import pandas  # noqa: F401
        import sklearn  # noqa: F401
        import streamlit  # noqa: F401

if __name__ == "__main__":
    unittest.main()
