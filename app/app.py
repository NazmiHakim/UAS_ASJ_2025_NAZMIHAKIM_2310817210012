import os
from flask import Flask, render_template, request, redirect, url_for, Response
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
        # Ambil parameter filter dari query string
        rank_filter = request.args.get('rank', '')
        gender_filter = request.args.get('gender', '')

        # Query dasar untuk pahlawan aktif
        query = Hero.query.filter_by(status='active')

        # Terapkan filter jika ada
        if rank_filter:
            query = query.filter_by(rank=rank_filter)
        if gender_filter:
            query = query.filter_by(gender=gender_filter)
        
        active_heroes = query.order_by(Hero.id).all()
        fallen_heroes = Hero.query.filter_by(status='fallen').order_by(Hero.id).all()
        
        # Kirim nilai filter ke template
        return render_template('index.html', heroes=active_heroes, fallen_heroes=fallen_heroes, rank_filter=rank_filter, gender_filter=gender_filter)


    @app.route('/add', methods=['POST'])
    def add():
        hero_name = request.form['hero_name']
        hero_title = request.form.get('hero_title')
        hero_race = request.form['hero_race']
        hero_skill = request.form['hero_skill']
        hero_gender = request.form['hero_gender']
        # Ambil rank dari form
        hero_rank = request.form['hero_rank']
        
        new_hero = Hero(name=hero_name, title=hero_title, race=hero_race, skill=hero_skill, gender=hero_gender, rank=hero_rank)

        photo = request.files.get('hero_photo')
        if photo and photo.filename != '':
            new_hero.photo = photo.read()
            new_hero.photo_mimetype = photo.mimetype

        try:
            db.session.add(new_hero)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f'Terjadi masalah saat merekrut pahlawan baru: {e}'

    @app.route('/hero/photo/<int:id>')
    def hero_photo(id):
        hero = Hero.query.get_or_404(id)
        if not hero.photo:
            # Jika tidak ada foto, tampilkan default
            return app.send_static_file('resources/default.png')
        
        return Response(hero.photo, mimetype=hero.photo_mimetype)

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
                Hero.query.filter(Hero.id.in_(ids_to_delete)).delete(synchronize_session=False)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
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
            hero_to_edit.gender = request.form['hero_gender']
            # Perbarui rank dari form
            hero_to_edit.rank = request.form['hero_rank']

            photo = request.files.get('hero_photo')
            if photo and photo.filename != '':
                hero_to_edit.photo = photo.read()
                hero_to_edit.photo_mimetype = photo.mimetype

            try:
                db.session.commit()
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                return f'Terjadi masalah saat memperbarui data pahlawan: {e}'
        else:
            return render_template('edit.html', hero=hero_to_edit)

    return app