
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command, prompt_bool
from app import app, db

migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from flask_database import manager as database_manager
manager.add_command('database', database_manager)

if __name__ == '__main__':
    manager.run()