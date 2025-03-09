from mistralai import Mistral
import os
from pathlib import Path
import json
from mistralai import DocumentURLChunk, ImageURLChunk, TextChunk
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


# Create a csv file with the following columns: file_name, text, link
with open("data.csv", "w") as file:
    file.write("file_name, text, link\n")

# all links on ethnopharmacologia_pdf_links.txt
pdf_links = []
with open("ethnopharmacologia_pdf_links.txt", "r") as file:
    pdf_links.extend(line.strip() for line in file)

# get all the files in the directory data_correct
pdf_files = list(Path("data_correct").glob("*.pdf"))


for pdf_file in tqdm(pdf_files):
    assert pdf_file.is_file()
    link = next(
            (pdf_link for pdf_link in pdf_links if pdf_file.stem.replace("data_correct/", "") in pdf_link), None
    )
    try:
        uploaded_file = client.files.upload(
                file={
                        "file_name": pdf_file.stem,
                        "content": pdf_file.read_bytes(),
                },
                purpose="ocr",
        )

        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

        pdf_response = client.ocr.process(document=DocumentURLChunk(document_url=signed_url.url), model="mistral-ocr-latest", include_image_base64=True)

        response_dict = json.loads(pdf_response.model_dump_json())
        json_string = json.dumps(response_dict, indent=4)
        # save on csv file
        with open("data.csv", "a") as file:
            file.write(f"{pdf_file.stem}, {json_string}, {link}\n")
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")






