from app import app, db

with app.app_context():
    db.create_all()
    print("Tables created successfully.")


#command: python create_db.py