from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from config import basedir


def get_env():
    """
    Figure out environment from the application path
    """
    if 'test' in basedir:
        return 'test'
    if 'revmic' in basedir:
        return 'prod'
    if 'michael' in basedir:
        return 'dev'
    return 'default'

app = create_app(get_env())
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()
