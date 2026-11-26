import os
from app import create_app
from app.extensions import db
from seeds.seed_data import seed_database

app = create_app()


@app.cli.command("seed-db")
def seed_db_command():
    """Seeds the database with default admin, categories, packages, add-ons, and showcases."""
    with app.app_context():
        seed_database()
        print("Database seeding completed successfully.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed on startup if database is empty
        from app.models import AdminUser
        if not AdminUser.query.first():
            print("Empty database detected. Running seed...")
            seed_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
