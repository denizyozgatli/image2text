import requests
from io import BytesIO
from PIL import Image
import google.generativeai as genai

class ImageTextExtractor:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Hata: GOOGLE_API_KEY sağlanmadı.")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _clean_extracted_text(self, text, user_prompt):
        if text.startswith(user_prompt):
            text = text[len(user_prompt):].strip()

        common_starters = [
            "İşte metnin tamamı:", "Metin aşağıdadır:", "Elbette, resimdeki metin şu şekildedir:",
            "Resimdeki metin:", "Metin:", "İşte metin:", "Resimde görünen metin şudur:",
            "İşte resimdeki metnin tam transkripsiyonu:", "Elbette, resimdeki metin şudur:",
            "Aşağıdaki metin resimde yer almaktadır:", "Elbette, resimdeki tüm metni şöyle çıkarıyorum:",
            "Burada resimden çıkarılan metin var:", "Elbette, aşağıdaki resimdeki metni çıkardım:",
            "Görseldeki metin:", "Resimden çıkarılan metin:", "İşte resmin içindeki tüm metin:",
            "İşte resimdeki tüm metnin transkripsiyonu:", "İşte resmi alıntının tam metni:",
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


    def _load_image(self, path_or_url_or_bytes):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        if isinstance(path_or_url_or_bytes, str):
            path_or_url = path_or_url_or_bytes
            if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
                response = requests.get(path_or_url, headers=headers)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(path_or_url)
        else:
            img = Image.open(path_or_url_or_bytes)
            
        return img

    def extract_text(self, image_input):
        user_prompt = "Bu resimdeki tüm metni çıkar."

        img = self._load_image(image_input)
        
        response = self.model.generate_content([user_prompt, img])
        extracted_text = response.text
        cleaned_text = self._clean_extracted_text(extracted_text, user_prompt)

        return cleaned_text
