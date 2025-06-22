import streamlit as st
from imagetotext import ImageTextExtractor
from PIL import Image

st.set_page_config(page_title="Resimden Metin Çıkarıcı", page_icon="📄")

st.title("Resimden Metin Çıkarıcı")
st.write("Google Gemini AI kullanarak bir resimdeki metinleri çıkarın.")
st.write("---")

try:
    api_key = st.secrets["secrets"]["GOOGLE_API_KEY"]
    extractor = ImageTextExtractor(api_key=api_key)
except Exception:
    st.error("Hata: GOOGLE_API_KEY bulunamadı. Lütfen Streamlit Cloud'a 'Secret' olarak eklediğinizden emin olun.")
    st.stop()

source_option = st.radio(
    "Resim Kaynağını Seçin:",
    ('Dosya Yükle', 'URL ile Belirt')
)

image_file = None
image_url = ""

if source_option == 'Dosya Yükle':
    image_file = st.file_uploader("Metin çıkarılacak resmi yükleyin...", type=["jpg", "jpeg", "png", "webp"])
elif source_option == 'URL ile Belirt':
    image_url = st.text_input("Resmin URL'sini buraya yapıştırın:")

if st.button("Metni Çıkar", type="primary"):
    if image_file:
        st.image(image_file, caption="Yüklenen Resim", use_container_width=True)
        with st.spinner('Metin çıkarılıyor, lütfen bekleyin...'):
            extracted_text = extractor.extract_text(image_file)
            
            st.subheader("Çıkarılan Metin:")
            st.text_area(label="", value=extracted_text, height=300)

            st.download_button(
                label="Metni .txt Olarak İndir",
                data=extracted_text.encode('utf-8'),
                file_name='cikarilan_metin.txt',
                mime='text/plain'
            )

    elif image_url:
        with st.spinner('URL\'den resim indiriliyor ve metin çıkarılıyor...'):
            try:
                st.image(image_url, caption="URL'den Gelen Resim", use_container_width=True)
                extracted_text = extractor.extract_text(image_url)

                st.subheader("Çıkarılan Metin:")
                st.text_area(label="", value=extracted_text, height=300)

                st.download_button(
                    label="Metni .txt Olarak İndir",
                    data=extracted_text.encode('utf-8'),
                    file_name='cikarilan_metin.txt',
                    mime='text/plain'
                )
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
    else:
        st.warning("Lütfen bir resim dosyası yükleyin veya bir URL girin.")
