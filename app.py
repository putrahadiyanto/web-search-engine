from flask import Flask, request, render_template, jsonify
import logging
from core.search_keyword import search_string
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
            
            # Execute the search using the search_string function
            try:
                results = search_string(
                    keyword=keyword,
                    start_url=seed_url,
                    max_depth=depth_limit,
                    max_width=width_limit,
                    timeout=10
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

@app.route('/search_ajax', methods=['POST'])
def search_ajax():
    """AJAX endpoint for keyword search"""
    data = request.get_json()
    
    seed_url = data.get('seed_url', '')
    if not seed_url:  # If empty string provided, use default
        seed_url = 'http://upi.edu'
        
    keyword = data.get('keyword', '')
    depth_limit = int(data.get('depth_limit', 3))
    width_limit = int(data.get('width_limit', 5))
    
    if seed_url and not seed_url.startswith(('http://', 'https://')):
        seed_url = 'http://' + seed_url
    
    # Execute the search
    try:
        # Check if we're looking for route information for a specific URL
        target_url = data.get('target_url', None)
        
        # This will store progress updates
        app.config['CRAWL_PROGRESS'] = {
            'current_depth': 0,
            'current_width': 0,
            'max_depth': depth_limit,
            'max_width': width_limit,
            'current_url': '',
            'total_visited': 0,
            'matched_count': 0
        }
        
        # If we're looking for a specific route
        if target_url:
            # For now, we'll just return the basic info we have
            # In a full implementation, this would trace the crawl path
            return jsonify({
                'status': 'success',
                'route': {
                    'url': target_url,
                    'steps': [
                        {'url': seed_url, 'depth': 0, 'title': 'Start URL'}
                    ]
                }
            })
        
        results = search_string(
            keyword=keyword,
            start_url=seed_url,
            max_depth=depth_limit,
            max_width=width_limit,
            timeout=10
        )
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results),
            'keyword': keyword,
            'seed_url': seed_url,
            'depth_limit': depth_limit,
            'width_limit': width_limit
        })
        
    except Exception as e:
        logger.error(f"AJAX search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

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