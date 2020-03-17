from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Init cors
CORS(app)

# Siswa Model


class Siswa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_kelas = db.Column(db.Integer)
    nis = db.Column(db.String(100))
    nama = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, id_kelas, nis, nama, jenis_kelamin, password):
        self.id_kelas = id_kelas
        self.nis = nis
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.password = password

# Siswa Schema


class SiswaSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_kelas', 'nis', 'nama', 'jenis_kelamin', 'password')


# Init Siswa Schema
siswa_schema = SiswaSchema()
siswas_schema = SiswaSchema(many=True)

# Get All Siswa
@app.route('/siswa', methods=['GET'])
def get_all_siswa():
    all_siswa = Siswa.query.all()
    result = siswas_schema.dump(all_siswa)

    return jsonify(result)

# Create a Siswa
@app.route('/siswa', methods=['POST'])
def add_siswa():
    id_kelas = request.json['id_kelas']
    nis = request.json['nis']
    nama = request.json['nama']
    jenis_kelamin = request.json['jenis_kelamin']
    password = request.json['password']

    new_siswa = Siswa(id_kelas, nis, nama, jenis_kelamin, password)
    db.session.add(new_siswa)
    db.session.commit()

    return siswa_schema.jsonify(new_siswa)

# Delete a Siswa
@app.route('/siswa/<id>', methods=['DELETE'])
def delete_siswa(id):
    siswa = Siswa.query.get(id)
    db.session.delete(siswa)
    db.session.commit()

    return siswa_schema.jsonify(siswa)

# Edit Siswa
@app.route('/siswa/<id>', methods=['PUT'])
def update_siswa(id):
    siswa = Siswa.query.get(id)

    siswa.id_kelas = request.json['id_kelas']
    siswa.nis = request.json['nis']
    siswa.nama = request.json['nama']
    siswa.jenis_kelamin = request.json['jenis_kelamin']
    siswa.password = request.json['password']

    db.session.commit()

    return siswa_schema.jsonify(siswa)

# Model Guru


class Guru(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(100), unique=True)
    nama = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, nip, nama, password):
        self.nip = nip
        self.nama = nama
        self.password = password

# Guru Schema


class GuruSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nip', 'nama', 'password')


# Init Guru Schema
guru_schema = GuruSchema()
gurus_schema = GuruSchema(many=true)

# Get All Guru
@app.route('/guru', methods=['GET'])
def get_all_guru():
    all_guru = Guru.query.all()
    result = gurus_schema.dump(all_guru)

    return jsonify(result)

# Auth Guru
@app.route('/auth/guru', methods=['POST'])
def auth_guru():
    nip = request.json['nip']
    password = request.json['password']

    guru = Guru.query.filter_by(nip=nip, password=password).first()

    return guru_schema.jsonify(guru)

# Get a Guru
@app.route('/guru/<id>', methods=['GET'])
def get_guru_by_id(id):
    guru = Guru.query.get(id)

    return guru_schema.jsonify(guru)

# Create a Guru
@app.route('/guru', methods=['POST'])
def add_guru():
    nip = request.json['nip']
    nama = request.json['nama']
    password = request.json['password']

    new_guru = Guru(nip, nama, password)
    db.session.add(new_guru)
    db.session.commit()

    return guru_schema.jsonify(new_guru)

# Delete a Guru
@app.route('/guru/<id>', methods=['DELETE'])
def delete_guru(id):
    guru = Guru.query.get(id)
    db.session.delete(guru)
    db.session.commit()

    return guru_schema.jsonify(guru)

# Edit Guru
@app.route('/guru/<id>', methods=['PUT'])
def update_guru(id):
    guru = Guru.query.get(id)

    guru.nip = request.json['nip']
    guru.nama = request.json['nama']
    guru.password = request.json['password']

    db.session.commit()

    return guru_schema.jsonify(guru)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
