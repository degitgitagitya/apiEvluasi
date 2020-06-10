from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os
import secrets
import numpy as np
import pandas as pd
import math

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
    nilai_pretest = db.Column(db.Integer)

    def __init__(self, id_kelas, nis, nama, jenis_kelamin, password, nilai_pretest):
        self.id_kelas = id_kelas
        self.nis = nis
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.password = password
        self.nilai_pretest = nilai_pretest


# Siswa Schema
class SiswaSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_kelas', 'nis', 'nama',
                  'jenis_kelamin', 'password', 'nilai_pretest')


# Init Siswa Schema
siswa_schema = SiswaSchema()
siswas_schema = SiswaSchema(many=True)

# Get All Siswa
@app.route('/siswa', methods=['GET'])
def get_all_siswa():
    all_siswa = Siswa.query.all()
    result = siswas_schema.dump(all_siswa)

    return jsonify(result)

# Auth Siswa
@app.route('/auth/siswa', methods=['POST'])
def auth_siswa():
    nis = request.json['nis']
    password = request.json['password']
    siswa = Siswa.query.filter_by(nis=nis, password=password).first()
    result = siswa_schema.dump(siswa)

    return jsonify(result)

# Get All Siswa by id_kelas
@app.route('/siswa/kelas/<id>', methods=['GET'])
def get_all_siswa_by_kelas(id):
    all_siswa = Siswa.query.filter_by(id_kelas=id)
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
    nilai_pretest = request.json['nilai_pretest']

    new_siswa = Siswa(id_kelas, nis, nama, jenis_kelamin,
                      password, nilai_pretest)
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
    siswa.nilai_pretest = request.json['nilai_pretest']

    db.session.commit()

    return siswa_schema.jsonify(siswa)

# Batch Upload Siswa
@app.route('/siswa/upload-batch/<int:id>', methods=['POST'])
def upload_batch_siswa(id):
    data = request.json['data']

    for i in data:
        new_siswa = Siswa(id, i['nis'], i['nama'], i['jenis_kelamin'], i['password'], 0)
        db.session.add(new_siswa)

    db.session.commit()

    all_siswa = Siswa.query.filter_by(id_kelas=id)
    result = siswas_schema.dump(all_siswa)

    return jsonify(result)


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
gurus_schema = GuruSchema(many=True)

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


# Kelas Model
class Kelas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.Integer)
    nama = db.Column(db.String(100))

    def __init__(self, id_guru, nama):
        self.id_guru = id_guru
        self.nama = nama


# Kelas Schema
class KelasSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_guru', 'nama')


# Init Kelas Schema
kelas_schema = KelasSchema()
kelases_schema = KelasSchema(many=True)

# Get All Kelas
@app.route('/kelas', methods=['GET'])
def get_kelases():
    all_kelas = Kelas.query.all()
    result = kelases_schema.dump(all_kelas)

    return jsonify(result)

# Get a Kelas
@app.route('/kelas/id/<id>', methods=['GET'])
def get_kelas_by_id(id):
    kelas = Kelas.query.get(id)

    return kelas_schema.jsonify(kelas)

# Get All Kelas By id_guru
@app.route('/kelas/<id_guru>', methods=['GET'])
def get_kelases_by_guru(id_guru):
    all_kelas = Kelas.query.filter_by(id_guru=id_guru)
    result = kelases_schema.dump(all_kelas)

    return jsonify(result)

# Create a Kelas
@app.route('/kelas', methods=['POST'])
def add_kelas():
    id_guru = request.json['id_guru']
    nama = request.json['nama']

    new_kelas = Kelas(id_guru, nama)
    db.session.add(new_kelas)
    db.session.commit()

    return kelas_schema.jsonify(new_kelas)

# Delete a Kelas
@app.route('/kelas/<id>', methods=['DELETE'])
def delete_kelas(id):
    kelas = Kelas.query.get(id)
    db.session.delete(kelas)
    db.session.commit()

    return kelas_schema.jsonify(kelas)

# Edit Kelas
@app.route('/kelas/<id>', methods=['PUT'])
def update_kelas(id):
    kelas = Kelas.query.get(id)

    kelas.id_guru = request.json['id_guru']
    kelas.nama = request.json['nama']

    db.session.commit()

    return kelas_schema.jsonify(kelas)


# Model Pre Test
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pertanyaan = db.Column(db.String(100))
    pilihan = db.relationship('PilihanTest', backref='test', lazy=True)


# Pre Test Schema
class TestSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pertanyaan')


# Init Test Schema
test_schema = TestSchema()
tests_schema = TestSchema(many=True)


# Schema Pilihan
class PilihanTestSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_test', 'pilihan', 'is_right')


# Schema Test Custom
class TestSchemaCustom(ma.Schema):
    class Meta:
        model = Test
        fields = ('id', 'pertanyaan', 'pilihan')
    pilihan = ma.Nested(PilihanTestSchema(many=True))


custom_test_schema = TestSchemaCustom()
many_custom_test_schema = TestSchemaCustom(many=True)

# Get All Test with Jawaban
@app.route('/alltest', methods=['GET'])
def get_all_test_with_option():
    all_test = Test.query.all()
    result = many_custom_test_schema.dump(all_test)

    return jsonify(result)

# Get All Test
@app.route('/test', methods=['GET'])
def get_all_test():
    all_test = Test.query.all()
    result = tests_schema.dump(all_test)

    return jsonify(result)

# Create a Test
@app.route('/test', methods=['POST'])
def add_test():
    pertanyaan = request.json['pertanyaan']

    new_test = Test(pertanyaan=pertanyaan)
    db.session.add(new_test)
    db.session.commit()

    return test_schema.jsonify(new_test)

# Delete a Test
@app.route('/test/<id>', methods=['DELETE'])
def delete_test(id):
    test = Test.query.get(id)
    db.session.delete(test)
    db.session.commit()

    return test_schema.jsonify(test)

# Edit a Test
@app.route('/test/<id>', methods=['PUT'])
def update_test(id):
    test = Test.query.get(id)

    test.pertanyaan = request.json['pertanyaan']

    db.session.commit()

    return test_schema.jsonify(test)


# Model Pilihan Test
class PilihanTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_test = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    pilihan = db.Column(db.String(100))
    is_right = db.Column(db.Integer)

    def __init__(self, id_test, pilihan, is_right):
        self.id_test = id_test
        self.pilihan = pilihan
        self.is_right = is_right


# Init pilihan schema
pilihan_test_schema = PilihanTestSchema()
many_pilihan_test_schema = PilihanTestSchema(many=True)

# Get All Pilihan Test
@app.route('/pilihantest', methods=['GET'])
def get_all_pilihan_test():
    all_pilihan_test = PilihanTest.query.all()
    result = many_pilihan_test_schema.dump(all_pilihan_test)

    return jsonify(result)

# Get All Kelas By id_test
@app.route('/pilihantest/<id_test>', methods=['GET'])
def get_all_pilihan_test_by_id_test(id_test):
    all_pilihan_test = PilihanTest.query.filter_by(id_test=id_test)
    result = many_pilihan_test_schema.dump(all_pilihan_test)

    return jsonify(result)

# Create a Pilihan Test
@app.route('/pilihantest', methods=['POST'])
def add_pilihan_test():
    id_test = request.json['id_test']
    pilihan = request.json['pilihan']
    is_right = request.json['is_right']

    new_pilihan_test = PilihanTest(id_test, pilihan, is_right)
    db.session.add(new_pilihan_test)
    db.session.commit()

    return pilihan_test_schema.jsonify(new_pilihan_test)

# Delete a pilihan Test
@app.route('/pilihantest/<id>', methods=['DELETE'])
def delete_pilihan_test(id):
    pilihan_test = PilihanTest.query.get(id)
    db.session.delete(pilihan_test)
    db.session.commit()

    return pilihan_test_schema.jsonify(pilihan_test)

# Edit a Pilihan Test
@app.route('/pilihantest/<id>', methods=['PUT'])
def edit_pilihan_test(id):
    pilihan_test = PilihanTest.query.get(id)

    pilihan_test.id_test = request.json['id_test']
    pilihan_test.pilihan = request.json['pilihan']
    pilihan_test.is_right = request.json['is_right']

    db.session.commit()

    return pilihan_test_schema.jsonify(pilihan_test)


# Model Token
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100))

    def __init__(self, token):
        self.token = token


# schema Token
class TokenSchema(ma.Schema):
    class Meta:
        fields = ('id', 'token')


# Init Schema Token
token_schema = TokenSchema()

# Get a Token
@app.route('/token/<id>', methods=['GET'])
def get_a_token(id):
    token = Token.query.get(id)
    result = token_schema.dump(token)

    return token_schema.jsonify(token)

# Update Token
@app.route('/token/<id>', methods=['PUT'])
def update_token(id):
    token = Token.query.get(id)
    token.token = secrets.token_hex(3)

    db.session.commit()

    return token_schema.jsonify(token)

# Auth Token
@app.route('/token/<id>', methods=['POST'])
def auth_token(id):
    temp = request.json['token']
    token = Token.query.filter_by(id=id, token=temp).first()
    result = token_schema.dump(token)

    return jsonify(result)


# Model Ujian
class Ujian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_kelas = db.Column(db.Integer)
    id_bank_soal = db.Column(db.Integer)
    mata_pelajaran = db.Column(db.String(100))
    status = db.Column(db.Integer)
    tanggal_tes = db.Column(db.String(100))
    waktu_selesai = db.Column(db.String(100))

    def __init__(self, id_kelas, id_bank_soal, mata_pelajaran, status, tanggal_tes, waktu_selesai):
        self.id_kelas = id_kelas
        self.id_bank_soal = id_bank_soal
        self.mata_pelajaran = mata_pelajaran
        self.status = status
        self.tanggal_tes = tanggal_tes
        self.waktu_selesai = waktu_selesai


# Ujian Schema
class UjianSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_kelas', 'id_bank_soal', 'mata_pelajaran', 'status', 'tanggal_tes', 'waktu_selesai')


# Init Ujian Schema
ujian_schema = UjianSchema()
many_ujian_schema = UjianSchema(many=True)

# Get All Ujian
@app.route('/ujian', methods=['GET'])
def get_ujian():
    all_ujian = Ujian.query.all()
    result = many_ujian_schema.dump(all_ujian)

    return jsonify(result)

# Get Active Ujian
@app.route('/ujian/active/<id_kelas>')
def get_active_ujian(id_kelas):
    ujian = Ujian.query.filter_by(id_kelas=id_kelas, status=1).first()

    return ujian_schema.jsonify(ujian)

# Get a Ujian
@app.route('/ujian/<id>', methods=['GET'])
def get_one_ujian(id):
    ujian = Ujian.query.get(id)

    return ujian_schema.jsonify(ujian)

# Create a Ujian
@app.route('/ujian', methods=['POST'])
def add_ujian():
    id_kelas = request.json['id_kelas']
    id_bank_soal = request.json['id_bank_soal']
    mata_pelajaran = request.json['mata_pelajaran']
    status = request.json['status']
    tanggal_tes = request.json['tanggal_tes']
    waktu_selesai = request.json['waktu_selesai']

    new_ujian = Ujian(id_kelas, id_bank_soal, mata_pelajaran, status, tanggal_tes, waktu_selesai)
    db.session.add(new_ujian)
    db.session.commit()

    return ujian_schema.jsonify(new_ujian)

# Delete a Ujian
@app.route('/ujian/<id>', methods=['DELETE'])
def delete_ujian(id):
    ujian = Ujian.query.get(id)
    db.session.delete(ujian)
    db.session.commit()

    return ujian_schema.jsonify(ujian)

# Edit Ujian
@app.route('/ujian/<id>', methods=['PUT'])
def update_ujian(id):
    ujian = Ujian.query.get(id)

    ujian.id_kelas = request.json['id_kelas']
    ujian.id_bank_soal = request.json['id_bank_soal']
    ujian.mata_pelajaran = request.json['mata_pelajaran']
    ujian.status = request.json['status']
    ujian.tanggal_tes = request.json['tanggal_tes']
    ujian.waktu_selesai = request.json['waktu_selesai']

    db.session.commit()

    return ujian_schema.jsonify(ujian)


# Model Bank Soal
class BankSoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))

    def __init__(self, nama):
        self.nama = nama


# Schema Bank Soal
class BankSoalSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nama')


# Init Bank Soal Schema
bank_soal_schema = BankSoalSchema()
many_bank_soal_schema = BankSoalSchema(many=True)

# Get All Bank Soal
@app.route('/bank-soal', methods=['GET'])
def get_bank_soal():
    all_bank_soal = BankSoal.query.all()
    result = many_bank_soal_schema.dump(all_bank_soal)

    return jsonify(result)

# Get a Bank Soal
@app.route('/bank-soal/<id>', methods=['GET'])
def get_one_bank_soal(id):
    bank_soal = BankSoal.query.get(id)

    return bank_soal_schema.jsonify(bank_soal)

# Create Bank Soal
@app.route('/bank-soal', methods=['POST'])
def add_bank_soal():
    nama = request.json['nama']

    new_bank_soal = BankSoal(nama)
    db.session.add(new_bank_soal)
    db.session.commit()

    return bank_soal_schema.jsonify(new_bank_soal)

# Delete Bank Soal
@app.route('/bank-soal/<id>', methods=['DELETE'])
def delete_bank_soal(id):
    bank_soal = BankSoal.query.get(id)
    db.session.delete(bank_soal)
    db.session.commit()

    return bank_soal_schema.jsonify(bank_soal)

# Edit Bank Soal
@app.route('/bank-soal/<id>', methods=['PUT'])
def update_bank_soal(id):
    bank_soal = BankSoal.query.get(id)

    bank_soal.nama = request.json['nama']

    db.session.commit()

    return bank_soal_schema.jsonify(bank_soal)


# Model Soal
class Soal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_bank_soal = db.Column(db.Integer)
    pertanyaan = db.Column(db.String(500))
    pilihan = db.relationship('PilihanSoal', backref='soal', lazy=True)


class SoalSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_bank_soal', 'pertanyaan')


soal_schema = SoalSchema()
many_soal_schema = SoalSchema(many=True)


# Schema Pilihan Soal
class PilihanSoalSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_soal', 'pilihan', 'is_right', 'analisis', 'keterangan')


# Schema Soal Custom
class SoalSchemaCustom(ma.Schema):
    class Meta:
        model = Soal
        fields = ('id', 'id_bank_soal', 'pertanyaan', 'pilihan')
    pilihan = ma.Nested(PilihanSoalSchema(many=True))


custom_soal_schema = SoalSchemaCustom()
many_custom_soal_schema = SoalSchemaCustom(many=True)


# Get All Soal by id_bank_soal with Pilihan
@app.route('/soal/bank-soal/<id_bank_soal>', methods=['GET'])
def get_soal_by_bank_pilihan(id_bank_soal):
    all_soal = Soal.query.filter_by(id_bank_soal=id_bank_soal)
    result = many_custom_soal_schema.dump(all_soal)

    return jsonify(result)

# Get All Soal by id_bank_soal
@app.route('/soal/<id_bank_soal>', methods=['GET'])
def get_soal_by_bank(id_bank_soal):
    all_soal = Soal.query.filter_by(id_bank_soal=id_bank_soal)
    result = many_soal_schema.dump(all_soal)

    return jsonify(result)

# Create Soal
@app.route('/soal', methods=['POST'])
def add_soal():
    id_bank_soal = request.json['id_bank_soal']
    pertanyaan = request.json['pertanyaan']

    new_soal = Soal(id_bank_soal=id_bank_soal, pertanyaan=pertanyaan)
    db.session.add(new_soal)
    db.session.commit()

    return soal_schema.jsonify(new_soal)

# Delete Soal
@app.route('/soal/<id>', methods=['DELETE'])
def delete_soal(id):
    soal = Soal.query.get(id)
    db.session.delete(soal)
    db.session.commit()

    return soal_schema.jsonify(soal)

# Edit Soal
@app.route('/soal/<id>', methods=['PUT'])
def update_soal(id):
    soal = Soal.query.get(id)

    soal.id_bank_soal = request.json['id_bank_soal']
    soal.pertanyaan = request.json['pertanyaan']

    db.session.commit()

    return soal_schema.jsonify(soal)

# Upload Batch Soal
@app.route('/soal/upload-batch/<int:id>', methods=['POST'])
def upload_batch_soal(id):
    data = request.json['data']

    for i in data:
        new_soal = Soal(id_bank_soal=id, pertanyaan=i['pertanyaan'])
        db.session.add(new_soal)

    db.session.commit()

    all_soal = Soal.query.filter_by(id_bank_soal=id)
    result = many_soal_schema.dump(all_soal)

    return jsonify(result)


# Model Pilihan Soal
class PilihanSoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_soal = db.Column(db.Integer, db.ForeignKey('soal.id'), nullable=False)
    pilihan = db.Column(db.String(100))
    is_right = db.Column(db.Integer)
    analisis = db.Column(db.String(100))
    keterangan = db.Column(db.String(100))

    def __init__(self, id_soal, pilihan, is_right, analisis, keterangan):
        self.id_soal = id_soal
        self.pilihan = pilihan
        self.is_right = is_right
        self.analisis = analisis
        self.keterangan = keterangan


# Init Pilihan Soal Schema
pilihan_soal_schema = PilihanSoalSchema()
many_pilihan_soal_schema = PilihanSoalSchema(many=True)

# Get All Pilihan Soal
@app.route('/pilihan-soal', methods=['GET'])
def get_all_pilihan_soal():
    all_pilihan_soal = PilihanSoal.query.all()
    result = many_pilihan_soal_schema.dump(all_pilihan_soal)

    return jsonify(result)

# Get All Pilihan Soal by id_soal
@app.route('/pilihan-soal/<id_soal>', methods=['GET'])
def get_all_pilihan_soal_by_id_soal(id_soal):
    all_pilihan_soal = PilihanSoal.query.filter_by(id_soal=id_soal)
    result = many_pilihan_soal_schema.dump(all_pilihan_soal)

    return jsonify(result)

# Create Pilihan Soal
@app.route('/pilihan-soal', methods=['POST'])
def add_pilihan_soal():
    id_soal = request.json['id_soal']
    pilihan = request.json['pilihan']
    is_right = request.json['is_right']
    analisis = request.json['analisis']
    keterangan = request.json['keterangan']

    new_pilihan_soal = PilihanSoal(id_soal, pilihan, is_right, analisis, keterangan)
    db.session.add(new_pilihan_soal)
    db.session.commit()

    return pilihan_soal_schema.jsonify(new_pilihan_soal)

# Delete Pilihan Soal
@app.route('/pilihan-soal/<id>', methods=['DELETE'])
def delete_pilihan_soal(id):
    pilihan_soal = PilihanSoal.query.get(id)
    db.session.delete(pilihan_soal)
    db.session.commit()

    return pilihan_soal_schema.jsonify(pilihan_soal)

# Edit a Pilihan Soal
@app.route('/pilihan-soal/<id>', methods=['PUT'])
def edit_pilihan_soal(id):
    pilihan_soal = PilihanSoal.query.get(id)

    pilihan_soal.id_soal = request.json['id_soal']
    pilihan_soal.pilihan = request.json['pilihan']
    pilihan_soal.is_right = request.json['is_right']
    pilihan_soal.analisis = request.json['analisis']
    pilihan_soal.keterangan = request.json['keterangan']

    db.session.commit()

    return pilihan_soal_schema.jsonify(pilihan_soal)

# Upload Batch Pilihan SOal
@app.route('/pilihan-soal/upload-batch/<int:id>', methods=['POST'])
def upload_batch_pilihan_soal(id):
    data = request.json['data']

    for i in data:
        new_pilihan_soal = PilihanSoal(id, i['pilihan'], i['is_right'], i['analisis'], i['keterangan'])
        db.session.add(new_pilihan_soal)

    db.session.commit()

    all_pilihan_soal = PilihanSoal.query.filter_by(id_soal=id)
    result = many_pilihan_soal_schema.dump(all_pilihan_soal)

    return jsonify(result)


# Model Jawaban
class Jawaban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer)
    id_ujian = db.Column(db.Integer)
    id_soal = db.Column(db.Integer)
    jawaban = db.Column(db.String(100))
    kunci = db.Column(db.String(100))
    analisis = db.Column(db.String(100))
    keterangan = db.Column(db.String(100))
    status = db.Column(db.Integer)

    def __init__(self, id_siswa, id_ujian, id_soal, jawaban, kunci, analisis, keterangan, status):
        self.id_siswa = id_siswa
        self.id_ujian = id_ujian
        self.id_soal = id_soal
        self.jawaban = jawaban
        self.kunci = kunci
        self.analisis = analisis
        self.keterangan = keterangan
        self.status = status


# Jawaban Schema
class JawabanSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_siswa', 'id_ujian', 'id_soal', 'jawaban', 'kunci', 'analisis', 'keterangan', 'status')


# Init Jawaban Schema
jawaban_schema = JawabanSchema()
many_jawaban_schema = JawabanSchema(many=True)


# Get All Jawaban
@app.route('/jawaban', methods=['GET'])
def get_jawaban():
    all_jawaban = Jawaban.query.all()
    result = many_jawaban_schema.dump(all_jawaban)

    return jsonify(result)

# Get All Jawaban Siswa
@app.route('/jawaban/siswa/<id_siswa>/<id_ujian>', methods=['GET'])
def get_jawaban_siswa(id_siswa, id_ujian):
    all_jawaban = Jawaban.query.filter_by(id_siswa=id_siswa, id_ujian=id_ujian)
    result = many_jawaban_schema.dump(all_jawaban)

    return jsonify(result)

# Add Jawaban
@app.route('/jawaban', methods=['POST'])
def add_jawaban():
    id_siswa = request.json['id_siswa']
    id_ujian = request.json['id_ujian']
    id_soal = request.json['id_soal']
    jawaban = request.json['jawaban']
    kunci = request.json['kunci']
    analisis = request.json['analisis']
    keterangan = request.json['keterangan']
    status = request.json['status']

    new_jawaban = Jawaban(id_siswa, id_ujian, id_soal, jawaban, kunci, analisis, keterangan, status)
    db.session.add(new_jawaban)
    db.session.commit()

    return jawaban_schema.jsonify(new_jawaban)

# Delete Jawaban
@app.route('/jawaban/<id>', methods=['DELETE'])
def delete_jawaban(id):
    jawaban = Jawaban.query.get(id)
    db.session.delete(jawaban)
    db.session.commit()

    return jawaban_schema.jsonify(jawaban)


# Model Hasil Manual
class HasilManual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer)
    id_kelas = db.Column(db.Integer)
    id_soal = db.Column(db.Integer)
    id_bank_soal = db.Column(db.Integer)
    status = db.Column(db.Integer)
    b = db.Column(db.Float)
    a = db.Column(db.Float)
    l = db.Column(db.Float)
    el = db.Column(db.Float)
    p = db.Column(db.Float)

    def __init__(self, id_siswa, id_kelas, id_soal, id_bank_soal, status, b, a, l, el, p):
        self.id_siswa = id_siswa
        self.id_kelas = id_kelas
        self.id_soal = id_soal
        self.id_bank_soal = id_bank_soal
        self.status = status
        self.b = b
        self.a = a
        self.l = l
        self.el = el
        self.p = p


# Schema Hasil Manual
class HasilManualSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_siswa', 'id_kelas', 'id_soal',
                  'id_bank_soal', 'status', 'b', 'a', 'l', 'el', 'p')


# Init Hasil Manual Schema
hasil_manual_schema = HasilManualSchema()
many_hasil_manual_schema = HasilManualSchema(many=True)

# Get All Hasil Manual by id_kelas
@app.route('/hasil-manual/<id_kelas>/<id_soal>/<id_bank_soal>', methods=['GET'])
def get_hasil_manual_by_id_kelas(id_kelas, id_soal, id_bank_soal):
    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)
    result = many_hasil_manual_schema.dump(hasil_manual)

    return jsonify(result)


# Sync with id_kelas
@app.route('/hasil-manual/sync/<id_kelas>/<id_soal>/<id_bank_soal>', methods=['POST'])
def sync_hasil_manual_by_id_kelas(id_kelas, id_soal, id_bank_soal):
    all_siswa = Siswa.query.filter_by(id_kelas=id_kelas)
    result = siswas_schema.dump(all_siswa)

    for i in result:
        temp = HasilManual(i['id'], id_kelas, id_soal,
                           id_bank_soal, 0, 0, 0, 0, 0, 0)
        db.session.add(temp)
        db.session.commit()

    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)
    new_result = many_hasil_manual_schema.dump(hasil_manual)

    return jsonify(new_result)

# Change Hasil Manual Status
@app.route('/hasil-manual/status/<id>/<status>', methods=['PUT'])
def change_status_hasil_manual(id, status):
    hasil_manual = HasilManual.query.get(id)
    hasil_manual.status = status

    db.session.commit()

    return hasil_manual_schema.jsonify(hasil_manual)

# Hard Refresh
@app.route('/hasil-manual/hard-refresh/<id_kelas>/<id_soal>/<id_bank_soal>', methods=['DELETE'])
def hard_refresh_hasil_manual(id_kelas, id_soal, id_bank_soal):
    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)

    for x in hasil_manual:
        db.session.delete(x)
        db.session.commit()

    all_siswa = Siswa.query.filter_by(id_kelas=id_kelas)
    result = siswas_schema.dump(all_siswa)

    for i in result:
        temp = HasilManual(i['id'], id_kelas, id_soal,
                           id_bank_soal, 0, 0, 0, 0, 0, 0)
        db.session.add(temp)
        db.session.commit()

    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)
    new_result = many_hasil_manual_schema.dump(hasil_manual)

    return jsonify(new_result)

# Batch update Hasil Manual
@app.route('/hasil-manual/batch-update/<id_kelas>/<id_soal>/<id_bank_soal>', methods=['PUT'])
def batch_update_hasil_manual(id_kelas, id_soal, id_bank_soal):
    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)

    data = request.json['data']
    index = 0

    for i in data:
        temp = HasilManual.query.get(hasil_manual[index].id)
        temp.status = i['status']
        db.session.commit()
        index = index + 1


    hasil_manual = HasilManual.query.filter_by(
        id_kelas=id_kelas, id_soal=id_soal, id_bank_soal=id_bank_soal)
    result = many_hasil_manual_schema.dump(hasil_manual)

    return jsonify(result)


# Model Bobot
class Bobot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_kelas = db.Column(db.Integer)
    id_soal = db.Column(db.Integer)
    pertanyaan = db.Column(db.String(300))
    id_bank_soal = db.Column(db.Integer)
    b = db.Column(db.Float)
    a = db.Column(db.Float)
    l = db.Column(db.Float)
    el = db.Column(db.Float)
    p = db.Column(db.Float)
    cluster = db.Column(db.Integer)

    def __init__(self, id_kelas, id_soal, pertanyaan, id_bank_soal, b, a, l, el, p, cluster):
        self.id_kelas = id_kelas
        self.id_soal = id_soal
        self.pertanyaan = pertanyaan
        self.id_bank_soal = id_bank_soal
        self.b = b
        self.a = a
        self.l = l
        self.el = el
        self.p = p
        self.cluster = cluster


# Schema Bobot
class BobotSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_kelas', 'id_soal', 'pertanyaan',
                  'id_bank_soal', 'b', 'a', 'l', 'el', 'p', 'cluster')


# Init Schema Bobot
bobot_schema = BobotSchema()
many_bobot_schema = BobotSchema(many=True)

# Get All Bobot by id_kelas id_soal id_bank_soal
@app.route('/bobot/<id_kelas>/<id_bank_soal>', methods=['GET'])
def get_all_bobot_custom(id_kelas, id_bank_soal):
    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    return jsonify(result)

# Sync Bobot
@app.route('/bobot/sync/<id_kelas>/<id_bank_soal>', methods=['POST'])
def sync_bobot(id_kelas, id_bank_soal):
    all_soal = Soal.query.filter_by(id_bank_soal=id_bank_soal)
    result = many_soal_schema.dump(all_soal)

    for i in result:
        temp = Bobot(id_kelas, i['id'], i['pertanyaan'],
                     id_bank_soal, 0, 0, 0, 0, 0, 0)
        db.session.add(temp)
        db.session.commit()

    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    return jsonify(result)

# Hard refresh bobot
@app.route('/bobot/hard-refresh/<id_kelas>/<id_bank_soal>', methods=['DELETE'])
def hard_refresh_bobot(id_kelas, id_bank_soal):
    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    
    for x in bobot:
        db.session.delete(x)
        db.session.commit()

    all_soal = Soal.query.filter_by(id_bank_soal=id_bank_soal)
    result = many_soal_schema.dump(all_soal)

    for i in result:
        temp = Bobot(id_kelas, i['id'], i['pertanyaan'],
                     id_bank_soal, 0, 0, 0, 0, 0, 0)
        db.session.add(temp)
        db.session.commit()

    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    return jsonify(result)

# Generate Bobot
@app.route('/bobot/generate/<id_kelas>/<id_bank_soal>', methods=['PUT'])
def generate_bobot(id_kelas, id_bank_soal):
    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    index_i = 0
    index_j = 0
    array_i = []
    array_j = []
    index_id_soal = []

   

    for i in result:
        hasil_manual = HasilManual.query.filter_by(
            id_kelas=i['id_kelas'], id_soal=i['id_soal'], id_bank_soal=i['id_bank_soal'])
        listHasilManual = many_hasil_manual_schema.dump(hasil_manual)
        index_id_soal.append(i['id'])

        jumlah_siswa = 0
        jumlah_jawaban_benar = 0
        jumlah_jawaban_salah = 0

        array_j = []

        for j in listHasilManual:
            array_j.append(j['status'])
            jumlah_siswa = jumlah_siswa + 1
            if (j['status'] == 1):
                jumlah_jawaban_benar = jumlah_jawaban_benar + 1
            else:
                jumlah_jawaban_salah = jumlah_jawaban_salah + 1
        
        array_i.append(array_j)

        b = jumlah_jawaban_benar / jumlah_siswa

        new_hasil_manual = Bobot.query.get(i['id'])
        new_hasil_manual.b = b
        db.session.commit()

    new_list = np.array(array_i)
    new_df = pd.DataFrame(data=new_list, index=index_id_soal)
    new_df['Jumlah'] = new_df.sum(axis=1)
    new_df = new_df.T
    new_df['Total'] = new_df.sum(axis=1)
    new_df = new_df.sort_values(by=['Total'])

    jumlah_soal = len(new_df)
    jumlah_per_kelompok = jumlah_soal // 3

    kelompok_awal = new_df[:jumlah_per_kelompok]
    kelompok_akhir = new_df[jumlah_per_kelompok*2+1: - 1]
    jumlah = new_df[-1:]
    

    kelompok_awal_sum = pd.DataFrame(data=kelompok_awal.sum(axis=0))
    kelompok_akhir_sum = pd.DataFrame(data=kelompok_akhir.sum(axis=0))
    jumlah = jumlah.T

    kelompok_awal_sum = kelompok_awal_sum.drop(['Total'])


    for index, row in kelompok_awal_sum.iterrows():
        a = kelompok_akhir_sum.loc[ index , : ].values
        b = row.values
        c = jumlah.loc[index, :].values
        if (c == 0):
            x = 0
        else:
            x = (2*(b - a)) / c

        new_hasil_manual = Bobot.query.get(index)
        new_hasil_manual.a = x
        db.session.commit()
        
        
    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    daftar_bobot = pd.DataFrame(result)

    daftar_bobot['l'] = daftar_bobot.apply(lambda x: x['a']*(2-x['b']), axis = 1)
    daftar_bobot['el'] = daftar_bobot.apply(lambda x: math.exp(x['l']), axis = 1)
    daftar_bobot['p'] = daftar_bobot.apply(lambda x: 1 / (1 + x['el']), axis = 1)

    for index, row in daftar_bobot.iterrows():
        l = row['l']
        el = row['el']
        p = row['p']
        id = row['id']

        new_hasil_manual = Bobot.query.get(id)
        new_hasil_manual.l = l
        new_hasil_manual.el = el
        new_hasil_manual.p = p
        db.session.commit()


    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)
    
    return (jsonify(result))

# Cluster
@app.route('/cluster/<id_kelas>/<id_bank_soal>', methods=['PUT'])
def cluster(id_kelas, id_bank_soal):
    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    array = []

    for i in result:
        array.append([i["a"], i["b"]])

    np_array = np.array(array)

    kmeans = KMeans(n_clusters=4, random_state=0).fit(np_array)

    index = 0

    for data in result:
        new_data = Bobot.query.get(data["id"])
        new_data.cluster = kmeans.labels_[index].item()
        db.session.commit()
        index = index + 1

    bobot = Bobot.query.filter_by(
        id_kelas=id_kelas, id_bank_soal=id_bank_soal)
    result = many_bobot_schema.dump(bobot)

    return (jsonify(result))


# Contoh CSV
# Download Contoh Siswa
@app.route('/file/siswa')
def get_file_siswa():
	return send_file('siswa.csv', as_attachment=True)

# Download Contoh Soal
@app.route('/file/soal')
def get_file_soal():
	return send_file('soal.csv', as_attachment=True)

# Download Contoh Pilihan Soal
@app.route('/file/pilihan-soal')
def get_file_pilihan_soal():
	return send_file('pilihansoal.csv', as_attachment=True)

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
