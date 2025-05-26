from flask import Flask, request, render_template
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from collections import deque

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)