from phoneDirectory import create_app, db
from phoneDirectory.models import Employee, Admin
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employee': Employee, 'Admin': Admin}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
