// PrivacyPolicy.tsx - Privacy Policy agreement page
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';
import './PrivacyPolicy.css';

export function PrivacyPolicy() {
    const [isAgreed, setIsAgreed] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const { user, refreshUser, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleAccept = async () => {
        if (!isAgreed) return;

        setError('');
        setIsLoading(true);

        try {
            await authApi.acceptPrivacyPolicy();
            await refreshUser();

            // Redirect to appropriate dashboard
            if (user?.role === 'educator') {
                navigate('/teacher/dashboard');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Gagal menyimpan persetujuan. Silakan coba lagi.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="privacy-policy-page">
            <div className="privacy-policy-container">
                <div className="privacy-policy-header">
                    <div className="logo">
                        <img src="/logo.png" alt="EduStart" className="logo-img" />
                        <span className="logo-text">EduStart</span>
                    </div>
                    <h1>📋 Kebijakan Privasi</h1>
                    <p>Mohon baca dan setujui kebijakan privasi kami</p>
                </div>

                <div className="privacy-policy-content">
                    <h2>1. Pengumpulan & Penggunaan Data oleh Kami (First Party Collection/Use)</h2>
                    <p>
                        EduStart mengumpulkan informasi yang Anda berikan secara langsung, termasuk:
                    </p>
                    <ul>
                        <li><strong>Data Akun:</strong> Nama, alamat email, dan kata sandi untuk autentikasi</li>
                        <li><strong>Data Profil Anak:</strong> Nama, usia, dan tingkat pendidikan untuk personalisasi pembelajaran</li>
                        <li><strong>Data Pembelajaran:</strong> Progres modul, jawaban kuis, waktu belajar, dan performa untuk analitik dan rekomendasi AI</li>
                        <li><strong>Data Teknis:</strong> Jenis perangkat, browser, dan alamat IP untuk keamanan dan peningkatan layanan</li>
                    </ul>
                    <p>
                        Kami menggunakan data ini untuk: menyediakan layanan pembelajaran, melacak kemajuan anak,
                        memberikan rekomendasi konten berbasis AI, dan meningkatkan kualitas platform.
                    </p>

                    <h2>2. Berbagi Data dengan Pihak Ketiga (Third Party Sharing/Collection)</h2>
                    <p>
                        Kami <strong>tidak menjual</strong> data pribadi Anda. Data mungkin dibagikan kepada:
                    </p>
                    <ul>
                        <li><strong>Penyedia Infrastruktur:</strong> Supabase (database & autentikasi) untuk menyimpan data dengan aman</li>
                        <li><strong>Layanan Analitik:</strong> Data anonim untuk analisis penggunaan platform</li>
                        <li><strong>Kewajiban Hukum:</strong> Jika diwajibkan oleh hukum atau perintah pengadilan</li>
                    </ul>
                    <p>
                        Semua penyedia pihak ketiga terikat kontrak untuk melindungi data Anda sesuai standar keamanan yang ketat.
                    </p>

                    <h2>3. Pilihan & Kontrol Pengguna (User Choice/Control)</h2>
                    <p>Anda memiliki kontrol penuh atas data Anda:</p>
                    <ul>
                        <li><strong>Notifikasi:</strong> Kelola preferensi email dan notifikasi di pengaturan akun</li>
                        <li><strong>Cookie:</strong> Atur preferensi cookie melalui browser Anda</li>
                        <li><strong>Menarik Persetujuan:</strong> Anda dapat menarik persetujuan kapan saja dengan menghubungi kami</li>
                        <li><strong>Opt-out Analitik:</strong> Nonaktifkan pengumpulan data analitik di pengaturan privasi</li>
                    </ul>

                    <h2>4. Akses, Edit, & Hapus Data (User Access, Edit, & Deletion)</h2>
                    <p>Anda berhak untuk:</p>
                    <ul>
                        <li><strong>Mengakses:</strong> Lihat semua data pribadi Anda dan anak melalui menu Pengaturan</li>
                        <li><strong>Mengedit:</strong> Perbarui informasi profil kapan saja</li>
                        <li><strong>Menghapus:</strong> Minta penghapusan akun dan semua data terkait melalui email ke privacy@edustart.id</li>
                        <li><strong>Ekspor:</strong> Unduh salinan data Anda dalam format yang dapat dibaca</li>
                    </ul>
                    <p>
                        Permintaan akan diproses dalam waktu 30 hari kerja sesuai regulasi yang berlaku.
                    </p>

                    <h2>5. Penyimpanan Data (Data Retention)</h2>
                    <p>Kebijakan penyimpanan data kami:</p>
                    <ul>
                        <li><strong>Data Akun Aktif:</strong> Disimpan selama akun aktif ditambah 1 tahun setelah penutupan</li>
                        <li><strong>Data Pembelajaran:</strong> Disimpan selama 3 tahun untuk analisis tren dan peningkatan AI</li>
                        <li><strong>Log Keamanan:</strong> Disimpan selama 1 tahun untuk audit keamanan</li>
                        <li><strong>Data Backup:</strong> Dihapus dalam 90 hari setelah data utama dihapus</li>
                    </ul>
                    <p>
                        Setelah periode retensi, data akan dihapus secara permanen atau dianonimkan.
                    </p>

                    <h2>6. Keamanan Data (Data Security)</h2>
                    <p>
                        Kami menerapkan langkah-langkah keamanan berlapis untuk melindungi data Anda:
                    </p>
                    <ul>
                        <li><strong>Enkripsi:</strong> Data dienkripsi saat transit (TLS 1.3) dan saat disimpan (AES-256)</li>
                        <li><strong>Autentikasi:</strong> Multi-factor authentication (MFA) tersedia untuk keamanan tambahan</li>
                        <li><strong>Akses Terbatas:</strong> Hanya personel berwenang yang dapat mengakses data sensitif</li>
                        <li><strong>Audit Rutin:</strong> Pemeriksaan keamanan berkala dan pengujian penetrasi</li>
                        <li><strong>Infrastruktur Aman:</strong> Server tersertifikasi dengan standar keamanan industri</li>
                    </ul>

                    <h2>7. Perubahan Kebijakan (Policy Change)</h2>
                    <p>
                        Kami dapat memperbarui kebijakan privasi ini sewaktu-waktu. Jika ada perubahan:
                    </p>
                    <ul>
                        <li><strong>Pemberitahuan:</strong> Kami akan mengirim email dan menampilkan notifikasi di aplikasi</li>
                        <li><strong>Persetujuan Ulang:</strong> Perubahan signifikan memerlukan persetujuan ulang Anda</li>
                        <li><strong>Riwayat Versi:</strong> Versi sebelumnya tersedia atas permintaan</li>
                    </ul>
                    <p>
                        Tanggal pembaruan terakhir akan selalu ditampilkan di bagian atas kebijakan ini.
                    </p>

                    <h2>8. Do Not Track (Sinyal Tidak Dilacak)</h2>
                    <p>
                        EduStart menghormati sinyal Do Not Track (DNT) dari browser Anda. Ketika DNT aktif:
                    </p>
                    <ul>
                        <li>Kami tidak akan mengumpulkan data analitik perilaku</li>
                        <li>Cookie non-esensial akan dinonaktifkan</li>
                        <li>Kami tidak melakukan pelacakan lintas situs</li>
                    </ul>
                    <p>
                        Catatan: Beberapa fitur personalisasi mungkin terbatas jika DNT diaktifkan.
                    </p>

                    <h2>9. Audiens Khusus & Internasional (International & Specific Audiences)</h2>
                    <h3>Perlindungan Anak (COPPA Compliance)</h3>
                    <p>
                        EduStart didesain untuk digunakan oleh anak-anak di bawah pengawasan orang tua. Kami mematuhi:
                    </p>
                    <ul>
                        <li>Persetujuan orang tua wajib sebelum pengumpulan data anak</li>
                        <li>Tidak ada iklan yang ditargetkan kepada anak-anak</li>
                        <li>Orang tua dapat meninjau dan menghapus data anak kapan saja</li>
                        <li>Data anak tidak dibagikan kepada pihak ketiga untuk pemasaran</li>
                    </ul>
                    <h3>Pengguna Indonesia</h3>
                    <p>
                        Kami mematuhi UU Perlindungan Data Pribadi (UU PDP) Indonesia, termasuk hak akses,
                        koreksi, dan penghapusan data.
                    </p>
                    <h3>Pengguna Uni Eropa (GDPR)</h3>
                    <p>
                        Pengguna EU memiliki hak tambahan termasuk portabilitas data dan hak untuk dilupakan.
                        Hubungi gdpr@edustart.id untuk permintaan terkait GDPR.
                    </p>

                    <h2>10. Informasi Tambahan (Other)</h2>
                    <h3>Tentang EduStart</h3>
                    <p>
                        EduStart adalah platform pembelajaran interaktif yang dirancang untuk membantu anak-anak
                        belajar dengan cara yang menyenangkan dan efektif. Kami berkomitmen untuk menjaga
                        privasi dan keamanan pengguna kami.
                    </p>
                    <h3>Hubungi Kami</h3>
                    <p>
                        Untuk pertanyaan tentang kebijakan privasi atau permintaan terkait data Anda:
                    </p>
                    <ul>
                        <li><strong>Email Umum:</strong> support@edustart.id</li>
                        <li><strong>Email Privasi:</strong> privacy@edustart.id</li>
                        <li><strong>Alamat:</strong> Yogyakarta, Indonesia</li>
                    </ul>
                    <p className="policy-date">
                        <em>Terakhir diperbarui: 6 Februari 2026</em>
                    </p>
                </div>

                {isAuthenticated && (
                    <div className="privacy-policy-actions">
                        {error && (
                            <div className="privacy-policy-error">
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <div className="privacy-policy-checkbox">
                            <input
                                type="checkbox"
                                id="agree-checkbox"
                                checked={isAgreed}
                                onChange={(e) => setIsAgreed(e.target.checked)}
                            />
                            <label htmlFor="agree-checkbox">
                                Saya telah membaca dan menyetujui Kebijakan Privasi EduStart
                            </label>
                        </div>

                        <button
                            className={`btn-agree ${isLoading ? 'loading' : ''}`}
                            onClick={handleAccept}
                            disabled={!isAgreed || isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <span className="spinner-small"></span>
                                    Menyimpan...
                                </>
                            ) : (
                                <>Setuju & Lanjutkan 🚀</>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
