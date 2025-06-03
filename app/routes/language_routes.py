"""
Language Routes
===============

Routes for handling language switching functionality.
"""

from flask import Blueprint, request, redirect, url_for, jsonify, session
from app.utils.language import set_language, get_language_info

language_bp = Blueprint('language', __name__)

@language_bp.route('/set-language/<language_code>')
def set_language_route(language_code):
    """
    Set the user's language preference
    
    Args:
        language_code (str): Language code (tr, en)
    
    Returns:
        Redirect to the referring page or dashboard
    """
    success = set_language(language_code)
    
    # Get the page to redirect to
    redirect_url = request.args.get('redirect', url_for('main.index'))
    
    if success:
        return redirect(redirect_url)
    else:
        # If language setting failed, redirect to dashboard
        return redirect(url_for('main.index'))

@language_bp.route('/api/language-info')
def language_info_api():
    """
    API endpoint to get language information
    
    Returns:
        JSON response with language information
    """
    return jsonify(get_language_info())

@language_bp.route('/api/set-language', methods=['POST'])
def set_language_api():
    """
    API endpoint to set language via POST request
    
    Returns:
        JSON response with success status
    """
    data = request.get_json()
    language_code = data.get('language') if data else None
    
    if not language_code:
        return jsonify({'success': False, 'error': 'Language code required'}), 400
    
    success = set_language(language_code)
    
    return jsonify({
        'success': success,
        'current_language': session.get('language', 'tr'),
        'message': 'Language updated successfully' if success else 'Invalid language code'
    }) 