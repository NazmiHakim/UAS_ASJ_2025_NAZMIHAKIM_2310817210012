import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, Hero


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
        # Mengambil data pahlawan berdasarkan status
        active_heroes = Hero.query.filter_by(status='active').order_by(Hero.id).all()
        fallen_heroes = Hero.query.filter_by(status='fallen').order_by(Hero.id).all()
        return render_template('index.html', heroes=active_heroes, fallen_heroes=fallen_heroes)

    @app.route('/add', methods=['POST'])
    def add():
        hero_name = request.form['hero_name']
        hero_title = request.form.get('hero_title')
        hero_race = request.form['hero_race']
        hero_skill = request.form['hero_skill']
        new_hero = Hero(name=hero_name, title=hero_title, race=hero_race, skill=hero_skill)
        try:
            db.session.add(new_hero)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f'Terjadi masalah saat merekrut pahlawan baru: {e}'

    @app.route('/hero/<int:id>')
    def detail(id):
        hero = Hero.query.get_or_404(id)
        return render_template('detail.html', hero=hero)

    @app.route('/fall/<int:id>')
    def fall(id):
        hero_to_fall = Hero.query.get_or_404(id)
        hero_to_fall.status = 'fallen'
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Terjadi masalah saat memindahkan pahlawan ke riwayat.'

    @app.route('/mass_delete', methods=['POST'])
    def mass_delete():
        ids_to_delete = request.form.getlist('ids')
        if ids_to_delete:
            try:
                for hero_id in ids_to_delete:
                    hero_to_delete = Hero.query.get(hero_id)
                    if hero_to_delete:
                        db.session.delete(hero_to_delete)
                db.session.commit()
            except Exception as e:
                return f'Terjadi masalah saat menghapus pahlawan secara massal: {e}'
        return redirect(url_for('index'))

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(id):
        hero_to_edit = Hero.query.get_or_404(id)
        if request.method == 'POST':
            hero_to_edit.name = request.form['hero_name']
            hero_to_edit.title = request.form.get('hero_title')
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