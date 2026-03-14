from flask import Blueprint

bp = Blueprint('chaves', __name__)

from app.chaves import routes  # noqa
