from flask import render_template, request
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', path=request.path, title='Not Found'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', path=request.path, title='Something Wrong'), 500
