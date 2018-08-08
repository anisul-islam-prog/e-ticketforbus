import os
import webbrowser

html = '<html> ...  generated html string ...</html>'
path = os.path.abspath('dummy.html')
url = 'file://' + path

with open(path, 'w') as f:
    f.write(html)
webbrowser.open(url)
