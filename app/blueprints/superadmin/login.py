__author__ = "Nigshoxiz"

from . import check_login
from . import super_admin_page

@super_admin_page.route("/login", methods=["GET"])
def login():
    pass
