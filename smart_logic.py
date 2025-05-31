#samrt_logic.py

def hitung_prioritas_smart(alternatif_data, kriteria_bobot, kriteria_type):
    """
    Menghitung pritoritas pasien menggunakan metode smart.
    
    Args: 
    alternatif_data (dict): Data pasien (alternatif),
                              format: {'Nama Paien': {'kriterian1': nilai, 'kriteria2': nilai, ...}}
    kriteria bobot (dict): Bobot untuk setiap kriteria,
                              format: {'kriteria1': bobot, 'kriteria2': bobot, ...}
    kriteria_type (dict): Tipe kriteria benefit/cost,
                              format: {'kriteria1': 'benefit', 'kriteria2': 'cost',...}
                              
    Returns:
    dict: prioritas pasien yang sudah di urutkan dari tertinggi hingga terendah,
          format: {'Nama Pasien': skor_prioritas, ...}
    """
    
    #1. kumpulkan semua nilai untuk setiap kriteria untuk normalisasi
    #   ini akan membantu kita menenmukan min dan max dari setiap kriteria
    kriteria_nilai_mentah = {kriteria: [] for kriteria in kriteria_bobot.keys()} #membuat dict kosong, mengisi nya dengan variabel sementara kriteria
    for pasien_nama, data in alternatif_data.items():                            #menguraikan dict alternatif_data dengan variabel sementara pasien_nama(keys) dan data(values)
        for kriteria, nilai_mentah in data.items():                              #menguraikan dict data yang didefinisikan pada iterasi sebelumnya dengan kriteria(keys) dan nilai_mentah(values)
            if kriteria in kriteria_nilai_mentah:                                #memastikan variabel sementara kriteria ada di dalam dict kriteria_nilai_mentah
                kriteria_nilai_mentah[kriteria].append(nilai_mentah)             #menambahkan nilai_mentah ke dalam list kriteria_nilai_mentah[kriteria]

    #2. Normalisasi nilai
    nilai_normalisasi = {}                                          #membuat dict kosong untuk menyimpan nilai normalisasi
    for pasien_nama, data in alternatif_data.items():               #menguraikan dict alternatif_data dengan variabel sementara pasien_nama(keys) dan data(values)
        nilai_normalisasi[pasien_nama] = {}                         #membuat dict kosong untuk menyimpan nilai normalisasi untuk setiap pasien dengan keys pasisen_nama dan values kosong
        for kriteria, nilai_mentah in data.items():                 #menguraikan dict data yang didefinisikan pada iterasi sebelumnya dengan kriteria(keys) dan nilai_mentah(values)
            if kriteria not in kriteria_bobot:                      #memasstikan kriteria yang didefinisikan dalam line sebelumnya tidak ada dalam dict kriteria_bobot 
                continue

            min_val = min(kriteria_nilai_mentah[kriteria])  #mendefinisikan nilai terkecil values dari setiap items dalam dict kriteria_nilai_mentah
            max_val = max(kriteria_nilai_mentah[kriteria])  #mendefinisakan nilai terbesar values dari setiap items dalam dict kriteria_nilai_sementara

            #Hindari pembagian dengan nol jika semua nilai sama
            if max_val - min_val == 0:
                normalized_score = 1.0 #Jka semua nilai sama, dianggap nilai terbaik
            else:
                if kriteria_type[kriteria] == 'benefit':
                    normalized_score = (nilai_mentah - min_val) / (max_val - min_val)
                elif kriteria_type[kriteria] == 'cost':
                    normalized_score = (max_val - nilai_mentah) / (max_val - min_val)
                else:
                    raise ValueError(f"Tipe Kriteria '{kriteria}' tidak valid. Harus 'benefit' atau 'cost")
            nilai_normalisasi[pasien_nama][kriteria] = normalized_score

    #3. hitung Nilai Akhir (Prioritas)
    prioritas_pasien = {}
    for pasien_nama, normalized_data in nilai_normalisasi.items():
        skor_akhir = 0
    for kriteria, skor_normalisasi in normalized_data.items():
        skor_akhir += skor_normalisasi * kriteria_bobot[kriteria]
    prioritas_pasien[pasien_nama] = skor_akhir

    #4. Urutkan pririoritas dari tertinggi ke terendah
    prioritas_terurut = dict(sorted(prioritas_pasien.items(), key=lambda item: item[1],reverse=True))

    return prioritas_terurut

#-----Data Contoh untuk Pengujian -----
#Definisiakan bobot krieria dan tipenya
bobot_kriteria = {
    "GCS": 0.30,
    "Tekanan jantung": 0.20,
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

#Definisikan data pasien
data_pasien = {
    "Pasien A": {"GCS": 15, "Tekanan Darah": 120, "Detak Jantung": 80, "Saturasi Oksigen": 98, "Nyeri": 2, "Usia": 35},
    "Pasien B": {"GCS": 8, "Tekanan Darah": 90, "Detak Jantung": 110, "Saturasi Oksigen": 88, "Nyeri": 7, "Usia": 60},
    "Pasien C": {"GCS": 12, "Tekanan Darah": 130, "Detak Jantung": 70, "Saturasi Oksigen": 95, "Nyeri": 4, "Usia": 20},
    "Pasien D": {"GCS": 5, "Tekanan Darah": 80, "Detak Jantung": 130, "Saturasi Oksigen": 80, "Nyeri": 9, "Usia": 75}
}

# --- Panggil Fungsi dan Cetak Hasil ---
if __name__ == "__main__": #ini memastikan kode di bawah hanya berjalan saat file ini dieksekusi langsung
    prioritas_hasil = hitung_prioritas_smart(data_pasien, bobot_kriteria, tipe_kriteria)

    print("--- Hasil Prioritas pasien ---")
    for pasien, skor in prioritas_hasil.items():
        print(f"{pasien}: {skor:.4f}") #cetak skor dengan 4 angka di belakang koma

    print("\n--- Data Normalisasi (untuk Pengecekan) ---")
    kriteria_nilai_mentah = {kriteria: [] for kriteria in bobot_kriteria.keys()}
    for pasien_nama, data in data_pasien.items():
        for kriteria, nilai_mentah in data.items():
            if kriteria in kriteria_nilai_mentah:
                kriteria_nilai_mentah[kriteria].append(nilai_mentah)

    nilai_normalisasi = {}
    for pasien_name, data in data_pasien.items():
        print(f"\nPasien: {pasien_name}")
        for kriteria, nilai_mentah in data.items():
            if kriteria not in bobot_kriteria:
                continue
            min_val = min(kriteria_nilai_mentah[kriteria])
            max_val = max(kriteria_nilai_mentah[kriteria])

            if max_val - min_val == 0:
                normalized_score = 1.0
            else:
                 if tipe_kriteria[kriteria] == 'benefit':
                    normalized_score = (nilai_mentah - min_val) / (max_val - min_val)
                 elif tipe_kriteria[kriteria] == 'cost':
                    normalized_score = (max_val - nilai_mentah) / (max_val - min_val)
            print(f"  {kriteria}: {nilai_mentah} (Normalisasi: {normalized_score:.4f})")
