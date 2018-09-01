import os,ui
file_path = 'map.html'
file_path = os.path.abspath(file_path)
w = ui.WebView()
w.load_url(file_path)
w.present()
