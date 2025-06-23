import os
from flask import Flask, render_template, request, redirect, url_for
from .models import db, Task


def create_app():
    app = Flask(__name__)

    # Konfigurasi Database dari Environment Variables
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("DB_HOST", "db") # 'db' adalah nama service di docker-compose

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Route untuk menampilkan semua tugas (Read)
    @app.route('/')
    def index():
        tasks = Task.query.all()
        return render_template('index.html', tasks=tasks)

    # Route untuk menambah tugas (Create)
    @app.route('/add', methods=['POST'])
    def add():
        content = request.form['task_content']
        new_task = Task(content=content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Terjadi masalah saat menambahkan tugas'

    # Route untuk menghapus tugas (Delete)
    @app.route('/delete/<int:id>')
    def delete(id):
        task_to_delete = Task.query.get_or_404(id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Terjadi masalah saat menghapus tugas'
            
    return app

if __name__ == "__main__":
    app = create_app()
    # Port 5000 adalah port di dalam container
    app.run(debug=True, host='0.0.0.0', port=5000)