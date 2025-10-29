# Kargo Risk Tahmin ve Raporlama Servisi (Black Box → RYPE)

## Proje Amacı
- Kaputt verileri kullanılarak lojistik risk tahmin modeli geliştirilecek ve ana veri tabanından farklı desenler keşfedilecek.  
- DF2_disruption_likelihood_score kullanılamadığında bile riskleri yönetebilecek şeffaf bir endeks (RYPE) oluşturulacak.  
- Akademik makale hazırlayarak literatürdeki dışsal risk faktörleri ve modelleme yöntemleri sunulacak.

## Ana Adımlar

### 1. Dış Veri Entegrasyonu
- Finansal volatilite, tedarikçi performansı ve jeopolitik istikrar gibi dış veri kaynakları modele dahil edilerek tahmin doğruluğu artırılır.  
- Amaç: Modelin yakalama oranını ve genel performansını yükseltmek.

### 2. Maliyet Odaklı Optimizasyon
- Yalnızca F1 skoruna odaklanmak yerine, yüksek risk kaçırıldığında maliyeti maksimize eden **cost-sensitive learning** uygulanır.  
- Amaç: Önemli risklerin gözden kaçmasını önlemek ve ekonomik kaybı minimize etmek.

### 3. Hassas Coğrafi Modelleme
- Mahalle veya ilçe düzeyinde **geospatial analizler** ile lojistik risk tahminleri hassaslaştırılır.  
- Bölge türü faktörlerinin etkisi model performansına entegre edilir.

### 4. RYPE Risk Endeksi Oluşturma
- **Manuel girdiler ve ağırlıklar:**  

| Metrik | Ağırlık | Açıklama |
|--------|--------|---------|
| MANUAL_FINANCE_HEALTH | 50% | Tedarikçi iflası riski |
| MANUAL_GEOPOLITICAL_RISK | 30% | Politik istikrarsızlık |
| MANUAL_CYBER_RISK | 20% | Siber saldırı riski |

- **Formül:**  
  `RYPE = 0.5*Finansal + 0.3*Jeopolitik + 0.2*Siber Risk`  
- **Uygulama Adımları:**  
  - df_model DataFrame’inde MANUAL_ ile başlayan sütunlar oluşturulur ve 0–1 arası varsayımsal skorlarla doldurulur.  
  - RYPE hesaplanır ve X matrisine (X_train, X_test) entegre edilir.  
  - Python / R / Julia / SQL kullanılarak hesaplama yapılır.  
  - XGBoost sınıflandırıcı ile test edilir ve model açıklanabilirliği artırılır (kara kutu kırılım formülü uygulanır).

### 5. Model Eğitimi ve Test
- RYPE ile zenginleştirilmiş veri setiyle XGBoost Classifier eğitilir.  
- Low/Moderate Risk sınıflandırma doğruluğu gözlemlenir ve sonuçlar analiz edilir.  
- Akademik makale için performans metrikleri, feature importance ve risk dağılımları raporlanır.

### 6. Akademik Makale Hazırlığı
- Literatürdeki risk faktörleri ve dışsal veri entegrasyonu detaylandırılır.  
- RYPE endeksinin, DF2 skoruna alternatif olarak risk tahmin performansını nasıl iyileştirdiği gösterilir.  
- Model açıklanabilirliği ve geospatial analizler, grafik ve tablolarla desteklenir.  
- Makale, tedarik zinciri risk yönetimi ve lojistikte yapay zeka uygulamalarına akademik katkı sağlar.

### 7. Ürün ve Sunum Çıktıları
- Model web sitesi ürününe dönüştürülür.  
- **Sunum ve görselleştirme:**  
  - PowerPoint (akademik ve tanıtım sunumları)  
  - Tableau / Power BI dashboard  
  - Ürün tanıtım videosu

### 8. Ticarileşme Planı
- **Aylık Paketler:** Temel, Orta, Kurumsal, Premium (500–7.000+ TL)  
- **Tek Seferlik Raporlar:** Basit / Detaylı (300–1.000 TL)  
- **Fiyatlandırma Stratejisi:**  
  - Başlangıçta düşük fiyatla pazar testi yapılır.  
  - Ek hizmetler (otomatik uyarılar, veri entegrasyonu, danışmanlık) ayrı ücretlendirilir.  
  - Değer bazlı fiyatlandırma ile kargo kaybı önlenmesi ve risk azaltım faydası göz önüne alınır.
