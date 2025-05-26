from flask import Flask, request, render_template
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        seed_url = request.form.get('seed_url', '')
        keyword = request.form.get('keyword', '')
        depth_limit = request.form.get('depth_limit', '')
        width_limit = request.form.get('width_limit', '')
        
        if seed_url and not seed_url.startswith(('http://', 'https://')):
            seed_url = 'http://' + seed_url
        
        log_message = f"Seed URL: {seed_url}, Keyword: {keyword}, Depth Limit: {depth_limit}, Width Limit: {width_limit}"
        logger.info(log_message)
        return render_template('index.html', seed_url=seed_url, keyword=keyword, depth_limit=depth_limit, width_limit=width_limit, message=log_message)
    

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)