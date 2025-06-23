import os
from flask import Flask, render_template, request, redirect, url_for
from .models import db, Hero


def create_app():
    app = Flask(__name__)

    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("DB_HOST", "db")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        # Mengambil semua data pahlawan
        heroes = Hero.query.order_by(Hero.id).all()
        # Mengirim list bernama 'heroes' ke template
        return render_template('index.html', heroes=heroes)

    @app.route('/add', methods=['POST'])
    def add():
        hero_name = request.form['hero_name']
        hero_race = request.form['hero_race']
        hero_skill = request.form['hero_skill']
        new_hero = Hero(name=hero_name, race=hero_race, skill=hero_skill)
        try:
            db.session.add(new_hero)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f'Terjadi masalah saat merekrut pahlawan baru: {e}'

    @app.route('/delete/<int:id>')
    def delete(id):
        hero_to_delete = Hero.query.get_or_404(id)
        try:
            db.session.delete(hero_to_delete)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Terjadi masalah saat menghapus catatan pahlawan'

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(id):
        hero_to_edit = Hero.query.get_or_404(id)
        if request.method == 'POST':
            hero_to_edit.name = request.form['hero_name']
            hero_to_edit.race = request.form['hero_race']
            hero_to_edit.skill = request.form['hero_skill']
            try:
                db.session.commit()
                return redirect(url_for('index'))
            except:
                return 'Terjadi masalah saat memperbarui data pahlawan'
        else:
            return render_template('edit.html', hero=hero_to_edit)

    return app