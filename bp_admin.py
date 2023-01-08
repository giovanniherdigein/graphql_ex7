from flask import (Blueprint, render_template, redirect, url_for, request)
from flask_login import login_required

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@login_required
def index():
    return render_template('admin.html')
