import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os

# ============================
#   1. KONFIGURASI HALAMAN & CSS
# ============================
st.set_page_config(page_title="Simulasi Listrik & PLTS", layout="wide")

def set_background(image_file):
    bg_img = 'none'
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        bg_img = f'url("data:image/png;base64,{data}")'

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: {bg_img}; 
            background-size: cover; 
            background-attachment: fixed; 
            background-color: #f0f2f6;
        }}
        /* SIDEBAR */
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255,255,255,0.95) !important; 
            border-right: 1px solid #ddd;
        }}
        section[data-testid="stSidebar"] * {{ color: #000 !important; }}
        
        /* CARD STYLE */
        .card {{
            background-color: #fff; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-left: 5px solid #0652DD;
        }}
        
        .main-title {{
            color: #0652DD !important; 
            font-weight: 900; 
            font-size: 2.5rem; 
            margin: 0;
        }}
        h3 {{ color: #0652DD !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Pastikan file gambar background ada di folder yang sama
set_background("110473958_p0.jpg")

# ============================
#   2. JUDUL
# ============================
st.markdown("<h1 class='main-title'>🔌 Simulasi Energi & PLTS Atap</h1>", unsafe_allow_html=True)
st.write("Hitung beban listrik rumah tangga dan simulasi investasi PLTS secara presisi.")
st.markdown("---")

# ============================
#   3. INPUT PERANGKAT (SIDEBAR)
# ============================
with st.sidebar:
    st.header("1. Input Perangkat")
    default_devices = {
        "Lampu LED (10W)": 10, "Kipas Angin (45W)": 45, "TV LED (80W)": 80,
        "Kulkas (120W)": 120, "Rice Cooker (350W)": 350, "Mesin Cuci (350W)": 350,
        "AC 1/2 PK (350W)": 350, "AC 1 PK (750W)": 750, "Setrika (1000W)": 1000,
        "Pompa Air (250W)": 250
    }
    device_name = st.selectbox("Pilih perangkat", list(default_devices.keys()))
    power = st.number_input("Daya (Watt)", value=default_devices[device_name])
    hours = st.number_input("Durasi (Jam/Hari)", 0.0, 24.0, 4.0)
    quantity = st.number_input("Jumlah", 1, 20, 1)

    if "data" not in st.session_state: st.session_state.data = []

    if st.button("Tambah Perangkat", type="primary"):
        st.session_state.data.append({
            "Perangkat": device_name, "Daya (W)": power,
            "Jam/Hari": hours, "Qty": quantity, "Total Wh": power * hours * quantity,
        })
    if st.button("Reset Data"): st.session_state.data = []

# ============================
#   4. ANALISIS BEBAN (LOAD)
# ============================
col_load, col_chart = st.columns([1.5, 1])
total_kwh_month = 0; cost_month = 0; tarif = 1444.70

with col_load:
    st.subheader("📊 Analisis Beban Listrik")
    tarif = st.number_input("Tarif Listrik (Rp/kWh)", value=1444.70)
    if len(st.session_state.data) > 0:
        df = pd.DataFrame(st.session_state.data)
        df["kWh/Hari"] = df["Total Wh"] / 1000
        st.dataframe(df, use_container_width=True)
        total_kwh_month = df["kWh/Hari"].sum() * 30
        cost_month = total_kwh_month * tarif
        st.markdown(f"""
        <div class="card">
            <h4>Total Konsumsi & Biaya</h4>
            <h2>{total_kwh_month:.1f} kWh <span style="font-size:16px">/ bln</span></h2>
            <h2 style="color:#27ae60;">Rp {cost_month:,.0f} <span style="font-size:16px">/ bln</span></h2>
        </div>""", unsafe_allow_html=True)
    else: st.info("Silakan tambahkan perangkat di sidebar.")

with col_chart:
    if len(st.session_state.data) > 0:
        st.subheader("Distribusi Energi")
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(df["kWh/Hari"], labels=df["Perangkat"], autopct="%1.1f%%", startangle=90, colors=plt.cm.Paired(range(len(df))))
        st.pyplot(fig)

st.markdown("---")

# ============================
#   5. SIMULASI PLTS (DETAIL)
# ============================
st.header("☀️ Simulasi & Konfigurasi PLTS")

if total_kwh_month > 0:
    # ---------------------------------------------------------
    # 1. PROFIL LISTRIK & LOKASI
    # ---------------------------------------------------------
    with st.expander("1️⃣ Profil Listrik & Lokasi", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            daya_pln = st.selectbox("Daya PLN (VA)", [450, 900, 1300, 2200, 3500, 4400, 5500, 6600, 10600], index=3)
            fasa = st.radio("Fasa", ["1 Phase", "3 Phase"], horizontal=True)
        with c2:
            lokasi_dict = {"Jakarta/Banten": 3.8, "Jawa Barat": 3.6, "Jawa Tengah": 3.9, "Jawa Timur": 4.2, "Luar Jawa (Rata2)": 4.0}
            lok_pilih = st.selectbox("Wilayah", list(lokasi_dict.keys()))
            peak_sun_hours = lokasi_dict[lok_pilih]
            st.info(f"Sun Hours: {peak_sun_hours} Jam/Hari")

    # ---------------------------------------------------------
    # 2. HARDWARE & TIPE SISTEM
    # ---------------------------------------------------------
    with st.expander("2️⃣ Tipe Sistem & Hardware", expanded=True):
        st.markdown("##### Pilih Konfigurasi:")
        system_mode = st.radio("Jenis Sistem:", ["On-Grid", "Hybrid", "Off-Grid"], horizontal=True)

        # Logika Deskripsi Sistem (Tanpa kode Image yang error)
        if system_mode == "On-Grid":
            st.info("💡 **On-Grid:** Hemat tagihan. Mati saat PLN mati. Tanpa Baterai.")
            # Jika Anda punya gambar diagram, aktifkan baris di bawah ini:
            # st.image("ongrid_diagram.jpg")
            use_battery = False
        elif system_mode == "Hybrid":
            st.warning("🔋 **Hybrid:** Hemat + Backup saat mati lampu. Pakai Baterai.")
            # st.image("hybrid_diagram.jpg")
            use_battery = True
        else:
            st.success("🏝️ **Off-Grid:** Mandiri (Di gunung/pulau). Wajib Baterai Besar.")
            # st.image("offgrid_diagram.jpg")
            use_battery = True

        c1, c2 = st.columns(2)
        with c1:
            panel_watt = st.number_input("Watt per Panel (Wp)", 100, 700, 550)
            jml_panel = st.number_input("Jumlah Panel", 1, 100, 8)
            sys_kwp = (panel_watt * jml_panel) / 1000
            st.caption(f"Kapasitas: **{sys_kwp:.2f} kWp**")
        with c2:
            batt_kwh = 0
            batt_type = "None"
            if use_battery:
                batt_type = st.selectbox("Tipe Baterai", ["Lithium (LiFePO4)", "Aki (Lead-Acid)"])
                saran = sys_kwp * 2 if system_mode == "Off-Grid" else sys_kwp
                batt_kwh = st.number_input("Kapasitas Baterai (kWh)", 1.0, 100.0, float(saran))
                st.caption(f"Est. Backup: {batt_kwh / ((total_kwh_month/30)/24):.1f} Jam")
            else:
                st.write("🚫 Tanpa Baterai")

    # ---------------------------------------------------------
    # 3. PARAMETER TEKNIS
    # ---------------------------------------------------------
    with st.expander("3️⃣ Parameter Teknis", expanded=False):
        c1, c2, c3 = st.columns(3)
        tilt = c1.slider("Tilt Angle", 0, 45, 15)
        shading = c2.slider("Shading Loss (%)", 0, 50, 5)
        eff = c3.slider("Efficiency (%)", 60, 95, 80)

    # HITUNGAN
    daily_prod = sys_kwp * peak_sun_hours * (eff/100) * (1 - shading/100)
    monthly_prod = daily_prod * 30
    
    # Harga
    p_panel = 14000000 if sys_kwp <= 5 else 13000000
    p_batt = 5500000 if "Lithium" in batt_type else 2500000
    capex = (sys_kwp * p_panel) + (batt_kwh * p_batt)
    
    savings = min(monthly_prod * tarif, cost_month)
    roi_thn = (capex / savings) / 12 if savings > 0 else 0

    # OUTPUT UTAMA
    st.subheader("📊 Hasil Simulasi")
    m1, m2, m3 = st.columns(3)
    m1.metric("Produksi (Est)", f"{monthly_prod:.1f} kWh/bln")
    m2.metric("Biaya (CAPEX)", f"Rp {capex:,.0f}")
    m3.metric("ROI", f"{roi_thn:.1f} Tahun", f"Hemat Rp {savings:,.0f}/bln")

    st.write("#### 📉 Proyeksi Cashflow")
    years = list(range(1, 26))
    df_roi = pd.DataFrame({"Tahun": years, "Penghematan": [savings*12*y for y in years], "Investasi": [capex]*25})
    st.line_chart(df_roi, x="Tahun", y=["Penghematan", "Investasi"], color=["#2ecc71", "#e74c3c"])

    # ---------------------------------------------------------
    # 4. ANALISIS KELEBIHAN & KEKURANGAN
    # ---------------------------------------------------------
    st.markdown("---")
    with st.expander("4️⃣ Analisis Kelebihan & Kekurangan Sistem", expanded=True):
        st.write(f"Berikut adalah analisis detail untuk sistem **{system_mode}** yang Anda pilih:")
        
        col_plus, col_minus = st.columns(2)
        
        # LOGIKA KONTEN BERDASARKAN SYSTEM MODE
        if system_mode == "On-Grid":
            pros = [
                "**Biaya Termurah:** Tidak perlu membeli baterai yang mahal.",
                "**ROI Tercepat:** Balik modal biasanya 5-7 tahun.",
                "**Bebas Perawatan:** Minim maintenance karena komponen sedikit.",
                "**Ekspor Listrik:** Sisa energi bisa diekspor ke PLN (jika meteran EXIM)."
            ]
            cons = [
                "**Tidak Ada Cadangan:** Listrik ikut mati total saat PLN padam (Anti-Islanding).",
                "**Birokrasi:** Wajib mengurus izin meteran EXIM ke PLN.",
                "**Ketergantungan:** Tidak bisa berfungsi di daerah tanpa jaringan PLN."
            ]
        
        elif system_mode == "Hybrid":
            pros = [
                "**Fleksibilitas:** Menikmati penghematan tagihan sekaligus punya cadangan daya.",
                "**Energy Security:** Lampu tetap nyala saat tetangga mati lampu.",
                "**Optimalisasi:** Bisa menyimpan energi siang hari untuk dipakai malam hari."
            ]
            cons = [
                "**Biaya Tinggi:** Komponen inverter hybrid dan baterai cukup mahal.",
                "**Maintenance Baterai:** Baterai memiliki umur pakai (5-10 tahun) dan harus diganti.",
                "**Kompleksitas:** Instalasi lebih rumit dibanding On-Grid."
            ]
            
        else: # Off-Grid
            pros = [
                "**100% Mandiri:** Tidak membayar tagihan listrik sama sekali.",
                "**Bebas Lokasi:** Bisa dipasang di gunung, pulau, atau hutan.",
                "**Kemandirian:** Tidak terdampak kenaikan tarif dasar listrik (TDL)."
            ]
            cons = [
                "**Biaya Sangat Mahal:** Butuh kapasitas baterai sangat besar (autonomy days).",
                "**Energi Terbuang:** Jika baterai penuh dan matahari terik, energi terbuang sia-sia.",
                "**Risiko Blackout:** Jika mendung berhari-hari, listrik bisa habis total."
            ]

        with col_plus:
            st.success("✅ **KELEBIHAN (PROS)**")
            for item in pros:
                st.markdown(f"- {item}")
        
        with col_minus:
            st.error("❌ **KEKURANGAN (CONS)**")
            for item in cons:
                st.markdown(f"- {item}")

else:
    st.info("👈 Masukkan data perangkat dulu.")