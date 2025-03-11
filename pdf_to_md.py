from mistralai import Mistral
import os
from pathlib import Path
import json
from mistralai import DocumentURLChunk, ImageURLChunk, TextChunk
from tqdm import tqdm
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Load environment variables from .env file
load_dotenv()


api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


# Create a sqlite database file with the following columns: file_name, text, link
# Define the base class for SQLAlchemy models
Base = declarative_base()

# Define the Document model
class Document(Base):
    __tablename__ = 'documents'

    id = sa.Column(sa.Integer, primary_key=True)
    file_name = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.Text)
    link = sa.Column(sa.String)

    def __repr__(self):
        return f"<Document(file_name='{self.file_name}')>"

# Create the database file
def create_database(db_path='documents.db'):
    # Create database directory if it doesn't exist
    db_dir = Path(db_path).parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True)

    # Create SQLite engine
    engine = sa.create_engine(f'sqlite:///{db_path}')

    # Create tables
    Base.metadata.create_all(engine)

    # Create session factory
    Session = sessionmaker(bind=engine)

    return engine, Session

# Initialize the database
engine, Session = create_database()

def save_document(file_name, text, link):
    session = Session()
    try:
        document = Document(file_name=file_name, text=text, link=link)
        session.add(document)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Database error: {str(e)}")
    finally:
        session.close()


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
        # Add to a sqlite database
        save_document(file_name=pdf_file.stem, text=json_string, link=link)
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")






