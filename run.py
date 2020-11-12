# -*- coding: UTF-8 -*-
"""
hello_flask: First Python-Flask webapp
"""
from app import app

if __name__ == '__main__':
  # Script executed directly?
    app.run(debug=True)  # Launch built-in web server and run this Flask webapp