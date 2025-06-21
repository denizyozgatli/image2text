import os
import re
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ImageTextExtractor:
    def __init__(self, model_name='gemini-1.5-flash'):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Hata: GOOGLE_API_KEY ortam değişkeni bulunamadı.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def _clean_extracted_text(self, text, user_prompt):
        if text.startswith(user_prompt):
            text = text[len(user_prompt):].strip()

        common_starters = [
            "İşte metnin tamamı:", "Metin aşağıdadır:",
            "Resimdeki metin:", "Metin:", "İşte metin:",
            "Aşağıdaki metin resimde yer almaktadır:",
            "Burada resimden çıkarılan metin var:",
            "Görseldeki metin:", "Resimden çıkarılan metin:",
            "İşte resimdeki tüm metnin transkripsiyonu:",
            "İşte metnin tam transkripsiyonu:",
            "Elbette, aşağıda resmin tam metni yer almaktadır:",
            "Tamam. İşte resimdeki metin:", "Transkript:", "Metin çıktı:", "Yazı:",
            "Resimdeki metin şu şekildedir:", "Resimde şu metin bulunmaktadır:",
            "İstediğiniz gibi, işte resimdeki metin:",
            "Resimden başarıyla çıkarılan metin:", "Görüntüden alınan metin:",
            "Resimdeki yazılar:", "İşte verilen görüntünün metni:",
            "İşte resmin metninin transkripsiyonu:",
            "İşte verilen resimdeki metnin tam transkripsiyonu:", "İşte istediğiniz metin:",
            "Elbette, istediğiniz metni size verebilirim:", "Elbette, işte istediğiniz metin:",
            "İşte resmin metin dökümü:", "Elbette, resmin tamamındaki metni şöyle alıyorum:",
            "İşte resmin tamamının metin yazısı:", "İşte görüntüdeki metin:"
        ]

        for starter in common_starters:
            if text.lower().startswith(starter.lower()):
                text = text[len(starter):].strip()
                break

        lines = text.splitlines()
        cleaned_lines = []
        previous_line_empty = False

        for line in lines:
            stripped_line = line.strip()
            if stripped_line == "":
                if not previous_line_empty:
                    cleaned_lines.append("")
                previous_line_empty = True
            else:
                cleaned_lines.append(stripped_line)
                previous_line_empty = False

        return "\n".join(cleaned_lines)

    def _load_image(self, path_or_url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
        }

        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            response = requests.get(path_or_url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"URL'den görsel alınamadı: HTTP {response.status_code}")
            img = Image.open(BytesIO(response.content))
            filename = path_or_url.split("/")[-1].split("?")[0]
            base_filename = re.sub(r'[^\w\-_.]', '_', filename)
        else:
            img = Image.open(path_or_url)
            base_filename = os.path.splitext(os.path.basename(path_or_url))[0]
        return img, base_filename

    def extract_text(self, image_path_or_url):
        user_prompt = "Bu resimdeki tüm metni çıkar."

        img, base_filename = self._load_image(image_path_or_url)
        print("Görsel yüklendi. Metin çıkarılıyor...")

        response = self.model.generate_content([user_prompt, img])
        extracted_text = response.text
        cleaned_text = self._clean_extracted_text(extracted_text, user_prompt)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_filename}_extracted_text_{timestamp}.txt"

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Metin başarıyla kaydedildi: {output_filename}")
        return output_filename