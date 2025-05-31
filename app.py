#app.py

from flask import Flask, render_template, request, redirect,url_for
#Import fungsi hitung_prioritas_smart dari dile smart_logic.py
from smart_logic import hitung_prioritas_smart

#buat objek aplikasi flask
app = Flask(__name__)

# --- Kriteria dan bobot (diidentifikasi di sini untuk kemudahan, nanti bisa diukur di DB) ---
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
# --- Akhiri Definisi Kriteria ---
# --- Routing ---
#Dekorator @app.route('/') menentukan URL mana yang akan memicu fungsi di bawahnya.
#dalam kasus ini, URL dasar aplikasi (misalnya http://127.0.0.1:5000/)
@app.route('/')
def index():
    return render_template('index.html')

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
        #Kita hanya mengirim satu pasien, tapi fingsinya dirancang untuk multiple.
        #Jadi kita kirimkan data_pasien_tunggal.
        prioritas_hasil = hitung_prioritas_smart(data_pasien_tunggal, bobot_kriteria, tipe_kriteria)

        #render template hasil_prioritas.html dan kirimkan data hasil_prioritas
        return render_template('result.html', prioritas_terurut=prioritas_hasil)

    # Jika bukan metode POST (misalnya user coba akses langsung /hitung_prioritas)
    return redirect(url_for('index')) # Kembali ke halaman input

# --- Menjalankan Aplikasi ---
#Bagian ini memastikan hanya berjalan saat file ini dieksekusi langsung
if __name__ == '__main__':
    # app.run() akan memulai server pengembangan flask
    #debug=True akan memberikan pesan error yang kebih detail dan reload server otomatis saat kode berubah.
    app.run(debug=True)
