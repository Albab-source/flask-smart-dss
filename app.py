#app.py

from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
#Import fungsi hitung_prioritas_smart dari dile smart_logic.py
from smart_logic import hitung_prioritas_smart, baca_csv_pasien_header
import os

#buat objek aplikasi flask
app = Flask(__name__)

# --- Konfigurasi Aplikasi ---
app.config['SECRET_KEY'] = 'ini_rahasia_anda_bisa_ganti_dengan_string_acak'
app.config['UPLOAD_FOLDER'] = 'datasets' # Nama folder untuk menyimpan file yang diunggah
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Batasi ukuran file hingga 16 MB
ALLOWED_EXTENSIONS = {'csv'} # Hanya izinkan file CSV

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --------- Kriteria dan bobot (diidentifikasi di sini untuk kemudahan, nanti bisa diukur di DB) ---------
#Ini harus konsisten dengan yang diharaokan oleh fungsi hitung_prioritas_smart anda
bobot_kriteria= {
    "GCS": 0.30,
    "Tekanan Darah": 0.20,
    "Detak Jantung": 0.15,
    "Saturasi Oksigen": 0.20,
    "Nyeri": 0.10,
    "Usia": 0.05
}

tipe_kriteria = {
    "GCS": "benefit",
    "Tekanan Darah": "benefit",
    "Detak Jantung": "benefit",
    "Saturasi Oksigen": "benefit",
    "Nyeri": "cost",
    "Usia": "cost"
}
# --------- Akhiri Definisi Kriteria ---------


# --------- Routing -----------
#Dekorator @app.route('/') menentukan URL mana yang akan memicu fungsi di bawahnya.
#dalam kasus ini, URL dasar aplikasi (misalnya http://127.0.0.1:5000/)

@app.route('/')
def index():
    return render_template('index.html', show_upload_option=True)

@app.route('/result', methods=['POST'])
def hitung_prioritas():
    #pastikan permintaan adalah POST (dari pengirim form)
    if request.method == 'POST':
        #ambil data dari form
        #request.form adalah dictionary yang berisi data dari input form
        nama_pasien = request.form['nama_pasien']

        #ubah data numerik menjadi float/int
        try:
            gcs = int(request.form['gcs'])
            tekanan_darah = int(request.form['tekanan_darah'])
            detak_jantung = int(request.form['detak_jantung'])
            saturasi_oksigen = int(request.form['saturasi_oksigen'])
            nyeri = int(request.form['nyeri'])
            usia = int(request.form['usia'])
        except ValueError:
            return "Input tidak valid. Pastikan semua nilai numerik diisi dengan benar.", 400 # bad Request
        
        #Sisipkan data pasien dalam format yang diharapkan fungsi SMART
        # data_pasien_tunggal dictionary untuk menyimpan data satu pasien
        data_pasien_tunggal = {
            nama_pasien: {
                "GCS": gcs,
                "Tekanan Darah": tekanan_darah,
                "Detak Jantung": detak_jantung,
                "Saturasi Oksigen": saturasi_oksigen,
                "Nyeri": nyeri,
                "Usia": usia
            }
        }

        #panggil fungsi hitung_prioritas_smart dari smart_logic.py
        #Kita hanya mengirim satu pasien, tapi fungsinya dirancang untuk multiple.
        #Jadi kita kirimkan data_pasien_tunggal.
        prioritas_hasil = hitung_prioritas_smart(data_pasien_tunggal, bobot_kriteria, tipe_kriteria)

        #render template hasil_prioritas.html dan kirimkan data hasil_prioritas
        return render_template('result.html', prioritas_terurut=prioritas_hasil)

    # Jika bukan metode POST (misalnya user coba akses langsung /hitung_prioritas)
    return redirect(url_for('index')) # Kembali ke halaman input


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if request.method == 'POST':

        #cek apakah ada file di request
        if 'file_csv' not in request.files:
            flash('Tidak ada bagian file.') # Pesan flash akan ditampilkan di template
            return redirect(url_for('index'))
        
        file = request.files['file_csv']

        # Jika user tidak memilih file, browser juga mengirimkna bagian kosong tanpa nama file.
        if file.filename =='':
            flash('Tidak ada file yang terpilih')
            return redirect(url_for('index'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path) # simapan file yang diunggah

            try:
                
                # Panggil fungsi baru untuk membaca hanya pada bagian heeader dari csv
                headers = baca_csv_pasien_header(file_path)

                # simpan path file dan headers di session untuk digunakan direquest selanjutnya
                session['uploaded_file_path'] = file_path
                session['csv_headers'] = headers

                # Redirect user ke halaman pemilihan kriteria (yang akan kita buat)
                return redirect(url_for('criteria_selection'))
            
            except Exception as e:
                flash(f'Terjadi kesalahan saat memproses file CSV: {e}')
                if os.path.exists(file_path):
                    os.remove(file_path) # hapus file jika ada error
                return redirect(url_for('index'))
        else:
            flash('Ekstensi file tidak diizinkan. hanya CSV yang diperbolehkan.')
            return redirect(url_for('index'))
            
    return redirect(url_for('index'))

@app.route('/criteria_selection')
def criteria_selection():
    # Ambil heaers dari session
    headers = session.get('csv_headers')
    if not headers:
        flash('Tidak ada data CSV yang diunggah. Silahkan unggah file terlebih dahulu.')
        return redirect(url_for('index'))
    # Render template untuk pemilihan kriteria dan kirimkan headers
    return render_template('criteria_selection.html', headers=headers)

# --- Menjalankan Aplikasi dalam Internal ---
#Bagian ini memastikan hanya berjalan saat file ini dieksekusi langsung
if __name__ == '__main__':
    # app.run() akan memulai server pengembangan flask
    #debug=True akan memberikan pesan error yang kebih detail dan reload server otomatis saat kode berubah.
    app.run(debug=True)
