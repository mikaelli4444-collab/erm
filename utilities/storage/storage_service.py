import uuid
import boto3
from botocore.client import Config


class StorageService:
    def __init__(self, config):
        self.bucket = config.storage.bucket_name
        self.endpoint = config.storage.endpoint_url
        self.access_key = config.storage.access_key
        self.secret_key = config.storage.secret_key
        self.base_url = config.storage.media_base_url

        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    def generate_filename(self, filename: str):
        ext = filename.split(".")[-1] #extrae la extension del archivo
        return f"{uuid.uuid4()}.{ext}" #genera un nombre unico para el archivo usando la extension original

    def upload_file(self, file): #llamar esta funcion para subir los archivos en el projects_services.py
        
        if file.content_type.startswith("image/"):
            folder = "images"

        elif file.content_type == "application/pdf":
            folder = "documents"

        elif file.content_type.startswith("video/"):
            folder = "videos"

        else:
            raise ValueError("Tipo de archivo no permitido")
                
        filename = self.generate_filename(file.filename)
        path = f"{folder}/{filename}" #construye ruta dentro del bucket, y ESTO es lo que se guarda en la db

        self.client.upload_fileobj( #subida real
            file.file,
            self.bucket,
            path,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        return path