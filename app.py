from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os
import secrets

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

    def __init__(self, id_kelas, id_bank_soal, mata_pelajaran, status, tanggal_tes):
        self.id_kelas = id_kelas
        self.id_bank_soal = id_bank_soal
        self.mata_pelajaran = mata_pelajaran
        self.status = status
        self.tanggal_tes = tanggal_tes


# Ujian Schema
class UjianSchema(ma.Schema):
    class Meta:
        fields = ('id', 'id_kelas', 'id_bank_soal',
                  'mata_pelajaran', 'status', 'tanggal_tes')


# Init Ujian Schema
ujian_schema = UjianSchema()
many_ujian_schema = UjianSchema(many=True)

# Get All Ujian
@app.route('/ujian', methods=['GET'])
def get_ujian():
    all_ujian = Ujian.query.all()
    result = many_ujian_schema.dump(all_ujian)

    return jsonify(result)

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

    new_ujian = Ujian(id_kelas, id_bank_soal,
                      mata_pelajaran, status, tanggal_tes)
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

    db.session.commit()

    return ujian_schema.jsonify(ujian)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
