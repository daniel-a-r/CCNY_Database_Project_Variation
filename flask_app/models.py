from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


user_album = db.Table('user_album', db.metadata,
                      db.Column('user_id', db.ForeignKey('user.id'), primary_key=True),
                      db.Column('album_id', db.ForeignKey('album.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    albums = db.relationship('Album', secondary=user_album, back_populates='users', lazy='dynamic')

    def __repr__(self):
        return f'User({self.name}, {self.email})'


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    spotify_artist_id = db.Column(db.String(50), nullable=False)
    spotify_artist_uri = db.Column(db.String(50), nullable=False)

    albums = db.relationship('Album', back_populates='artist', lazy='dynamic')

    def __repr__(self):
        return f'Artist({self.name})'


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_tracks = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    img_src = db.Column(db.String(100), nullable=False)
    spotify_album_id = db.Column(db.String(50), nullable=False)
    spotify_album_uri = db.Column(db.String(50), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)

    artist = db.relationship('Artist', back_populates='albums')
    tracks = db.relationship('AlbumTrack', back_populates='album', cascade="all, delete", lazy='dynamic')
    users = db.relationship('User', secondary=user_album, back_populates='albums', lazy='dynamic')

    def __repr__(self):
        return f'Album({self.name}, {self.total_tracks}, {self.duration}, {self.release_date}, {self.label}, {self.artist})'


class AlbumTrack(db.Model):
    __tablename__ = 'album_tracks'
    id = db.Column(db.Integer, primary_key=True)
    track_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    explicit = db.Column(db.Boolean, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    spotify_track_id = db.Column(db.String(50), nullable=False)
    spotify_track_uri = db.Column(db.String(50), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id', ondelete="CASCADE"), nullable=False)

    album = db.relationship('Album', back_populates='tracks')

    def __repr__(self):
        return f'AlbumTrack({self.track_number}, {self.name}, {self.explicit}, {self.duration}, {self.album})'

