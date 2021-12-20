from flask import redirect, url_for, render_template, flash
from flask_app import app, db, bcrypt, spotify
from flask_app.forms import RegisterForm, LoginForm, AlbumSearchForm, UpdateNameForm, UpdateEmailForm, UpdatePasswordForm
from flask_app.format_datetime import format_album_duration, format_track_duration, format_release_date
from flask_app.spotipy_wrapper import get_album_info
from flask_app.models import User, Artist, Album, AlbumTrack
from flask_login import login_user, current_user, logout_user, login_required
from pprint import pprint
from datetime import datetime, time


@app.route('/', methods=['GET', 'POST'])
@app.route('/home/', methods=['GET', 'POST'])
def home():
    search_results_list = []
    album_collection = []
    if current_user.is_authenticated:
        album_collection = current_user.albums.all()

    album_search_form = AlbumSearchForm()
    if album_search_form.validate_on_submit():
        album_name = album_search_form.album_name.data.strip().lower()
        spotify_results = spotify.search(q='album:' + f'{album_name}', limit=12, type='album')

        if spotify_results['albums']['total'] == 0:
            flash('No results. Try entering something different', 'warning')
        
        for item in spotify_results['albums']['items']:
            item_dict = {
                'artist': item['artists'][0]['name'],
                'id': item['id'],
                'img_src': item['images'][1]['url'],
                'name': item['name']
            }
            search_results_list.append(item_dict)

    return render_template('index.html', 
                           title='Album Search', 
                           form=album_search_form, 
                           results=search_results_list,
                           collection=album_collection, 
                           user_authenticated=current_user.is_authenticated)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Already logged in', 'warning')
        return redirect(url_for('home'))
    
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        form_email = register_form.email.data.lower()
        user = User.query.filter_by(email=form_email).first()
        if user:
            flash('Email already in use. Please use another', 'warning')
        else:
            form_name = register_form.name.data.strip()
            hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
            user = User(name=form_name.strip(), email=form_email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Account successfully created! You may now login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=register_form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already logged in', 'warning')
        return redirect(url_for('home'))
    
    login_form = LoginForm()
    if login_form.validate_on_submit():
        form_email = login_form.email.data
        form_password = login_form.password.data
        user = User.query.filter_by(email=form_email).first()

        if user and bcrypt.check_password_hash(user.password, form_password):
            login_user(user)
            flash('You may now start adding albums to your collection.', 'success')
            return redirect(url_for('home'))

    return render_template('login.html', title='Login', form=login_form)


@app.route('/add-to-collection/<string:spotify_album_id>', methods=['GET', 'POST'])
@login_required
def add_to_collection(spotify_album_id):
    #checks if the user is logged in
    if not current_user.is_authenticated:
        flash('Must be logged in to add to collection', 'warning')
        return redirect(url_for('login'))

    # checks if the artist is in the db already
    album_info = get_album_info(spotify_album_id)
    spotify_artist_id = album_info['album_artist']['spotify_artist_id']
    artist = Artist.query.filter_by(spotify_artist_id=spotify_artist_id).first()
    if not artist:
        artist = Artist(name=album_info['album_artist']['name'], 
                        spotify_artist_id=album_info['album_artist']['spotify_artist_id'],
                        spotify_artist_uri=album_info['album_artist']['spotify_artist_uri'])
        db.session.add(artist)
        db.session.commit()
    
    album = Album.query.filter_by(spotify_album_id=spotify_album_id).first()
    if not album:
        # convert album duration from string to time object
        album_duration = album_info['duration']
        album_duration = datetime.strptime(album_duration, '%H:%M:%S').time()

        album_release_date = album_info['release_date']
        album_release_date = datetime.strptime(album_release_date, '%Y-%m-%d').date()
        album = Album(name=album_info['name'],
                      total_tracks=album_info['total_tracks'],
                      duration=album_duration,
                      release_date=album_release_date,
                      label=album_info['label'],
                      img_src=album_info['img_src'],
                      spotify_album_id=album_info['spotify_album_id'],
                      spotify_album_uri=album_info['spotify_album_uri'],
                      artist_id=artist.id)
        db.session.add(album)
        db.session.commit()

        for track in album_info['tracks']:
            track_duration = track['duration']
            track_duration = datetime.strptime(track_duration, '%H:%M:%S').time()
            album_track = AlbumTrack(track_number=track['track_number'],
                                     name=track['name'],
                                     explicit=track['explicit'],
                                     duration=track_duration,
                                     spotify_track_id=track['spotify_track_id'],
                                     spotify_track_uri=track['spotify_track_uri'],
                                     album_id=album.id) 
            db.session.add(album_track)
        db.session.commit()
    
    user_album_found = current_user.albums.filter_by(id=album.id).first()
    if user_album_found:
        flash('Album already added to collection')            
    else:
        # insert into user_album
        current_user.albums.append(album)
        db.session.commit()
            
    return redirect(url_for('home'))


@app.route('/album_info/<int:album_id>', methods=['GET', 'POST'])
@login_required
def album_info_from_collection(album_id):
    album = Album.query.filter_by(id=album_id).first()
    album_tracks = AlbumTrack.query.filter_by(album_id=album_id).all()

    keys = ['db_album_id', 'artist_name', 'name', 'total_tracks', 'duration', 
            'release_date', 'label', 'img_src', 'spotify_album_id', 'spotify_artist_id']
    values = [album.id, album.artist.name, album.name, album.total_tracks, album.duration, 
              album.release_date, album.label, album.img_src, album.spotify_album_id, album.artist.spotify_artist_id]
    album_info = dict(zip(keys, values))

    album_info['duration'] = format_album_duration(album_info['duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])

    tracks = []
    for album_track in album_tracks:
        keys = ['track_number', 'name', 'explicit', 'duration']
        values = [album_track.track_number, album_track.name, album_track.explicit, album_track.duration]

        track = dict(zip(keys, values))
        track['duration'] = format_track_duration(track['duration'])
        tracks.append(track)

    in_collection = True

    return render_template('album_info.html', 
                           album_info=album_info, 
                           tracks=tracks, 
                           in_collection=in_collection, 
                           user_authenticated=current_user.is_authenticated)


@app.route('/album_info/<string:spotify_album_id>', methods=['GET', 'POST'])
def album_info_from_search(spotify_album_id):
    album_info = get_album_info(spotify_album_id)
    
    album_info['artist_name'] = album_info['album_artist']['name']
    album_info['spotify_artist_id'] = album_info['album_artist']['spotify_artist_id']
    album_info['duration'] = format_album_duration(album_info['duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])
    album_info.pop('spotify_album_uri', None)
    album_info.pop('album_artist', None)

    in_collection = False

    if not current_user.is_authenticated:
        in_collection = False
    else:
        #album_found = get_album_by_spotify_id(spotify_album_id)
        album = Album.query.filter_by(spotify_album_id=spotify_album_id).first()
        if album:
            album_info['db_album_id'] = album.id

            #user_album_found = get_user_album(album_info['db_album_id'])
            user_album_found = current_user.albums.filter_by(id=album.id).first()
            if user_album_found:
                in_collection = True
        else:
            in_collection = False

    album_tracks = album_info['tracks']
    for track in album_tracks:
        track['duration'] = format_track_duration(track['duration'])
        track.pop('spotify_track_id', None)
        track.pop('spotify_track_uri', None)

    album_info.pop('tracks', None)

    return render_template('album_info.html', 
                           album_info=album_info, 
                           tracks=album_tracks, 
                           in_collection=in_collection,
                           user_authenticated=current_user.is_authenticated)


@app.route('/remove-from-collection/<int:album_id>', methods=['GET', 'POST'])
@login_required
def remove_from_collection(album_id):
    if not current_user.is_authenticated:
        flash('Please login to perform that action', 'warning')
        return redirect(url_for('login'))
    
    #delete_from_collection(album_id)
    album = Album.query.filter_by(id=album_id).first()
    current_user.albums.remove(album)
    db.session.commit()

    users = album.users.all()
    artist = album.artist
    if not users:
        db.session.delete(album)
        db.session.commit()

    albums = artist.albums.all()
    if not albums:
        db.session.delete(artist)
        db.session.commit()

    return redirect(url_for('home'))


@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        flash('Must login to view profile', 'warning')
        return redirect(url_for('login'))

    update_name_form = UpdateNameForm()
    update_email_form = UpdateEmailForm()
    update_password_form = UpdatePasswordForm()

    if update_name_form.validate_on_submit():
        new_name = update_name_form.new_name.data
        current_user.name = new_name
        db.session.commit()
        flash('Name updated!', 'success')
        return redirect(url_for('profile'))

    if update_email_form.validate_on_submit():
        current_user.email = update_email_form.new_email.data
        db.session.commit()
        flash('Email updated!', 'success')
        return redirect(url_for('profile'))

    if update_password_form.validate_on_submit():
        new_hashed_password = bcrypt.generate_password_hash(update_password_form.new_password.data).decode('utf-8')
        current_user.password = new_hashed_password
        db.session.commit()
        flash('Password updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', 
                            title='Profile', 
                            update_name_form=update_name_form, 
                            update_email_form=update_email_form, 
                            update_password_form=update_password_form,
                            user_authenticated=current_user.is_authenticated,
                            current_user=current_user)


@app.route("/logout/")
def logout():
    logout_user()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for("home"))
