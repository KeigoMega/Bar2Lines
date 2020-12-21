from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

setup(
    console = [{
            'script': "main.py",
            'icon_resources': [(1, "images/BMP2LINES.ico")],
            }]
)
