from . import db

def initialize_db():
    db.init_db()
    db.insert_initial_data()