from app.controllers import get_all_accounts
from app.controllers import get_all_transactions
from app.controllers import create_requisitions
from app.controllers import delete_account
from app.controllers import update_transactions

from flask import Flask

app = Flask(__name__)
app.register_blueprint(get_all_accounts.blueprint, url_prefix = "/")
app.register_blueprint(get_all_transactions.blueprint, url_prefix = "/")
app.register_blueprint(create_requisitions.blueprint, url_prefix = "/")
app.register_blueprint(delete_account.blueprint, url_prefix = "/")
app.register_blueprint(update_transactions.blueprint, url_prefix = "/")


if __name__ == "__main__":
    app.run(debug=True)