from flask import Flask, request, render_template, jsonify
import logging
from core.crawler_bfs import bfs_crawl
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    seed_url = 'http://upi.edu'  # Default value
    keyword = ''
    depth_limit = 3
    width_limit = 5
    log_message = ""
    
    if request.method == 'POST':
        seed_url = request.form.get('seed_url', seed_url)
        keyword = request.form.get('keyword', '')
        depth_limit = int(request.form.get('depth_limit', depth_limit))
        width_limit = int(request.form.get('width_limit', width_limit))
        
        # Only proceed with search if a keyword is provided
        if keyword:
            if seed_url and not seed_url.startswith(('http://', 'https://')):
                seed_url = 'http://' + seed_url
            
            log_message = f"Searching for '{keyword}' starting from {seed_url} (depth: {depth_limit}, width: {width_limit})"
            logger.info(log_message)
            
            # Execute the search using bfs_crawl directly
            try:
                results = bfs_crawl(
                    start_url=seed_url,
                    max_depth=depth_limit,
                    max_width=width_limit,
                    timeout=10,
                    keyword=keyword
                )
                logger.info(f"Found {len(results)} results matching '{keyword}'")
            except Exception as e:
                error_message = f"An error occurred during search: {str(e)}"
                logger.error(error_message)
                return render_template('index.html', error=error_message)
        else:
            log_message = "Please enter a keyword to start searching."
        
        return render_template('index.html', 
                            seed_url=seed_url, 
                            keyword=keyword, 
                            depth_limit=depth_limit, 
                            width_limit=width_limit, 
                            message=log_message,
                            results=results)
    
    # For GET requests, just show the form without any default search
    return render_template('index.html', seed_url=seed_url, depth_limit=depth_limit, width_limit=width_limit)

@app.route('/get_progress', methods=['GET'])
def get_progress():
    """Endpoint to get the current crawling progress"""
    progress = app.config.get('CRAWL_PROGRESS', {
        'current_depth': 0,
        'current_width': 0,
        'max_depth': 0,
        'max_width': 0,
        'current_url': '',
        'total_visited': 0,
        'matched_count': 0
    })
    
    return jsonify(progress)

if __name__ == '__main__':
    app.run(debug=True)