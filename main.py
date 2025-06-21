from imagetotext import ImageTextExtractor

def main():
    image_path = input("Metin çıkarılacak resmin yolunu/linkini girin: ").strip('"').strip("'")
    extractor = ImageTextExtractor()
    extractor.extract_text(image_path)

if __name__ == "__main__":
    main()