from app import app, db, socketio
from app.models import *


if __name__ == "__main__":
    app.run(debug=True)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ItemForSale': ItemForSale, 'Category': Category, 'Address': Address,
            'followers': followers, 'user_addresses': user_addresses, 'Review': Review, 'Order': Order, 'OrderItem': OrderItem}
