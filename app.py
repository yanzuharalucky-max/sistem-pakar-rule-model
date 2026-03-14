from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ============================================================
# SIMULASI DATABASE
# ============================================================
users = {
    "admin": {"password": "admin", "nama": "Administrator"},
    "yodi": {"password": "12345", "nama": "Yodi Saputra"},
    "agus": {"password": "12345", "nama": "Agus Santoso"},
    "lucky": {"password": "12345", "nama": "Lucky Yan Zuhara"}
}

data_pasien = [
    {"id": 1, "nama": "Ahmad Pratama", "umur": 34, "jenis_kelamin": "Laki-laki", "alamat": "Jakarta", "riwayat": "Hipertensi"},
    {"id": 2, "nama": "Siti Nurhaliza", "umur": 28, "jenis_kelamin": "Perempuan", "alamat": "Bandung", "riwayat": "Asma"},
    {"id": 3, "nama": "Rudi Hartono", "umur": 45, "jenis_kelamin": "Laki-laki", "alamat": "Surabaya", "riwayat": "Diabetes"}
]

# ============================================================
# LAPORAN - Disimpan di file JSON agar tetap tersimpan
# ============================================================
LAPORAN_FILE = "laporan_data.json"

def load_laporan():
    if os.path.exists(LAPORAN_FILE):
        with open(LAPORAN_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_laporan(data):
    with open(LAPORAN_FILE, "w") as f:
        json.dump(data, f, indent=4)

laporan_data = load_laporan()

data_penyakit = [
    {"nama": "Pneumonia", "gejala": "Demam tinggi, batuk berdahak, nyeri dada, sesak napas.", "penanganan": "Antibiotik, istirahat cukup.", "pencegahan": "Vaksinasi, jaga kebersihan.", "detail": "Infeksi paru akibat bakteri, virus, atau jamur."},
    {"nama": "Bronkitis", "gejala": "Batuk berdahak, nyeri dada, kelelahan.", "penanganan": "Obat batuk, hindari asap.", "pencegahan": "Hindari rokok dan polusi.", "detail": "Peradangan pada saluran bronkial akibat infeksi atau iritasi."},
    {"nama": "Asma", "gejala": "Sesak napas, batuk malam hari, mengi.", "penanganan": "Inhaler, kontrol dokter rutin.", "pencegahan": "Hindari debu dan stres.", "detail": "Kondisi kronis yang menyebabkan penyempitan saluran udara."},
    {"nama": "TBC", "gejala": "Batuk lama, berat badan turun.", "penanganan": "Minum OAT selama 6 bulan.", "pencegahan": "Vaksin BCG, jaga imun tubuh.", "detail": "Infeksi paru akibat Mycobacterium tuberculosis."},
    {"nama": "Hipertensi", "gejala": "Pusing, tekanan darah tinggi.", "penanganan": "Obat antihipertensi, relaksasi.", "pencegahan": "Pola makan sehat.", "detail": "Tekanan darah tinggi kronis yang bisa memicu stroke."},
    {"nama": "Diabetes Mellitus", "gejala": "Gula darah tinggi, sering haus.", "penanganan": "Kontrol gula, obat & insulin.", "pencegahan": "Olahraga, diet seimbang.", "detail": "Kadar gula darah tinggi akibat kekurangan insulin."}
]

# ============================================================
# CONTEXT PROCESSOR
# ============================================================
@app.context_processor
def inject_counts():
    return dict(
        pasien_count=len(data_pasien),
        laporan_count=len(laporan_data)
    )

# ============================================================
# REGISTER
# ============================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not password or not confirm:
            flash("⚠️ Semua field wajib diisi!", "warning")
        elif username in users:
            flash("❌ Username sudah digunakan!", "danger")
        elif password != confirm:
            flash("⚠️ Konfirmasi password tidak cocok!", "warning")
        else:
            users[username] = {"password": password, "nama": username.title()}
            flash("✅ Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

# ============================================================
# LOGIN
# ============================================================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if username in users and users[username]["password"] == password:
            session["username"] = username
            session["nama"] = users[username]["nama"].title()
            flash(f"✅ Selamat datang, {session['nama']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Username atau password salah!", "danger")

    return render_template("login.html")

# ============================================================
# LOGOUT
# ============================================================
@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))

# ============================================================
# PROFIL
# ============================================================
@app.route("/profil")
def profil():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    nama = session.get("nama", users[username]["nama"].title())

    user_detail = {
        "username": username.title(),
        "nama": nama,
        "role": "Administrator" if username == "admin" else "User",
        "waktu_login": datetime.now().strftime("%d %B %Y, %H:%M"),
        "email": f"{username}@example.com"
    }
    return render_template("profil.html", user=user_detail, page="profil")

# ============================================================
# EDIT PROFIL
# ============================================================
@app.route("/edit_user", methods=["GET", "POST"])
def edit_user():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = users.get(username)

    if not user_data:
        flash("❌ Data user tidak ditemukan!", "danger")
        return redirect(url_for("logout"))

    if request.method == "POST":
        new_username = request.form.get("username", "").strip().lower()
        new_password = request.form.get("password", "").strip()
        new_nama = request.form.get("nama", user_data["nama"]).strip().title()

        if not new_username:
            flash("⚠️ Username tidak boleh kosong!", "warning")
            return redirect(url_for("edit_user"))

        users[new_username] = {
            "password": new_password if new_password else user_data["password"],
            "nama": new_nama
        }

        if new_username != username:
            users.pop(username, None)

        session["username"] = new_username
        session["nama"] = new_nama

        flash("✅ Profil berhasil diperbarui!", "success")
        return redirect(url_for("profil"))

    user_detail = {
        "username": username,
        "nama": user_data["nama"].title(),
        "email": f"{username}@example.com"
    }
    return render_template("edit_user.html", user=user_detail, page="profil")

# ============================================================
# DASHBOARD
# ============================================================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    nama = session["nama"]
    email = f"{username}@example.com"
    role = "Administrator" if username == "admin" else "User"

    return render_template("dashboard.html", username=nama.title(), email=email, role=role, page="dashboard")

# ============================================================
# DATA PASIEN
# ============================================================
@app.route("/data_pasien", methods=["GET", "POST"])
def data_pasien_view():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        umur = request.form.get("umur", "").strip()
        jk = request.form.get("jk", "").strip()
        alamat = request.form.get("alamat", "").strip()
        riwayat = request.form.get("riwayat", "").strip()

        if not nama or not umur or not jk or not alamat:
            flash("⚠️ Semua field wajib diisi!", "warning")
        else:
            try:
                umur_int = int(umur)
            except ValueError:
                flash("⚠️ Umur harus berupa angka!", "warning")
            else:
                new_id = (data_pasien[-1]["id"] if data_pasien else 0) + 1
                data_pasien.append({
                    "id": new_id,
                    "nama": nama.title(),
                    "umur": umur_int,
                    "jenis_kelamin": jk,
                    "alamat": alamat,
                    "riwayat": riwayat
                })
                flash("✅ Pasien berhasil ditambahkan!", "success")
                return redirect(url_for("data_pasien_view"))

    return render_template("data_pasien.html", data_pasien=data_pasien, username=session["nama"].title(), page="data_pasien")

# ============================================================
# 🩺 DIAGNOSA (PERBAIKAN PENYIMPANAN NAMA + OBAT + GEJALA)
# ============================================================
@app.route("/diagnosa", methods=["GET", "POST"])
def diagnosa_view():
    if "username" not in session:
        return redirect(url_for("login"))

    hasil = None
    obat = "-"
    if request.method == "POST":
        gejala = [request.form.get(f"gejala{i}", "").lower() for i in range(1, 6)]
        gejala_bersih = [g for g in gejala if g]
        text = " ".join(gejala_bersih)

        if not text:
            flash("⚠️ Silakan isi minimal satu gejala!", "warning")
        else:
            if any(word in text for word in ["batuk", "dahak", "nyeri dada", "sesak"]):
                hasil = "Bronkitis"
                obat = "Ambroxol, Paracetamol"
            elif any(word in text for word in ["demam", "paru", "menggigil", "nyeri dada"]):
                hasil = "Pneumonia"
                obat = "Amoxicillin, Ibuprofen"
            elif any(word in text for word in ["napas pendek", "mengi", "sesak"]):
                hasil = "Asma"
                obat = "Salbutamol Inhaler"
            elif any(word in text for word in ["batuk lama", "keringat malam", "berat badan turun"]):
                hasil = "TBC"
                obat = "Rifampisin, Isoniazid"
            elif any(word in text for word in ["tekanan darah tinggi", "pusing", "sakit kepala"]):
                hasil = "Hipertensi"
                obat = "Captopril, Amlodipine"
            elif any(word in text for word in ["gula darah", "sering haus", "sering kencing"]):
                hasil = "Diabetes Mellitus"
                obat = "Metformin, Insulin"
            else:
                hasil = "Sehat"
                obat = "Tidak perlu obat"

            # 🔧 Tambahan: pastikan nama user, gejala, dan obat tersimpan dengan benar
            nama_user = session.get("nama") or users.get(session["username"], {}).get("nama", "Tidak Diketahui")

            new_laporan = {
                "id": len(laporan_data) + 1,
                "nama": nama_user,
                "gejala": ", ".join(gejala_bersih),
                "hasil_diagnosa": hasil,
                "obat_direkomendasikan": obat,
                "tanggal": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            }

            laporan_data.append(new_laporan)
            save_laporan(laporan_data)
            flash(f"✅ Hasil diagnosa: {hasil}", "success")

    return render_template("diagnosa.html", username=session["nama"].title(), hasil=hasil, obat=obat, page="diagnosa")

# ============================================================
# LAPORAN
# ============================================================
@app.route("/laporan")
def laporan():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("laporan.html", laporan=laporan_data, username=session["nama"].title(), page="laporan")

@app.route("/hapus_laporan/<int:id>", methods=["POST"])
def hapus_laporan(id):
    global laporan_data
    laporan_data = [l for l in laporan_data if l["id"] != id]
    save_laporan(laporan_data)
    flash("🗑️ Laporan berhasil dihapus!", "success")
    return redirect(url_for("laporan"))

# ============================================================
# CETAK LAPORAN
# ============================================================
@app.route("/cetak_laporan")
def cetak_laporan():
    if "username" not in session:
        return redirect(url_for("login"))
    if not laporan_data:
        flash("⚠️ Belum ada laporan untuk dicetak.", "warning")
        return redirect(url_for("laporan"))
    response = make_response(render_template("laporan_cetak.html", laporan=laporan_data, username=session["nama"].title(), now=datetime.now().strftime("%d %B %Y, %H:%M")))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

# ============================================================
# STRUK PEMBAYARAN
# ============================================================
@app.route("/struk.html")
def struk():
    if "username" not in session:
        return redirect(url_for("login"))
    total = request.args.get("total", "0")
    uang = request.args.get("uang", "0")
    kembali = request.args.get("kembali", "0")

    return render_template("struk.html", total=total, uang=uang, kembali=kembali, username=session["nama"].title(), now=datetime.now().strftime("%d %B %Y, %H:%M"))

# ============================================================
# INFORMASI PENYAKIT
# ============================================================
@app.route("/informasi")
def informasi():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("informasi.html", username=session["nama"].title(), penyakit=data_penyakit, page="informasi")

@app.route("/informasi/<nama>")
def penyakit_detail(nama):
    if "username" not in session:
        return redirect(url_for("login"))
    penyakit = next((p for p in data_penyakit if p["nama"] == nama), None)
    if not penyakit:
        flash("Data penyakit tidak ditemukan.", "warning")
        return redirect(url_for("informasi"))
    return render_template("penyakit_detail.html", penyakit=penyakit, username=session["nama"].title(), page="informasi")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
