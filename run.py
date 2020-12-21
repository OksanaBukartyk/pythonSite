# -*- coding: UTF-8 -*-
"""
hello_flask: First Python-Flask webapp
"""
from app import create_app
from config import Config

if __name__ == '__main__':
  # Script executed directly?
    create_app(Config).run(debug=True)  # Launch built-in web server and run this Flask webapp