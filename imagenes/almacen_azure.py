"""Adaptador para Azure Blob Storage (Azurite en el laboratorio)."""

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    ContentSettings,
    generate_blob_sas,
)


class AlmacenAzure:
    """Guarda imágenes en un contenedor de Azure Blob Storage."""

    def __init__(self):
        cadena = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        partes = dict(
            fragmento.split("=", 1)
            for fragmento in cadena.split(";")
            if "=" in fragmento
        )

        self.cuenta = partes["AccountName"]
        self.clave_cuenta = partes["AccountKey"]
        self.contenedor_nombre = os.getenv(
            "AZURE_STORAGE_CONTAINER", "imagenes"
        )

        # El contenedor puede ver Azurite por su nombre dentro de Compose.
        self.blobs = BlobServiceClient.from_connection_string(
            cadena, api_version="2026-06-06"
        )
        self.contenedor = self.blobs.get_container_client(
            self.contenedor_nombre
        )

        try:
            self.contenedor.create_container()
        except ResourceExistsError:
            pass

        # La URL debe ser accesible desde el navegador del usuario.
        self.endpoint_publico = os.environ[
            "AZURE_PUBLIC_BLOB_ENDPOINT"
        ].rstrip("/")

    def subir(
        self, clave: str, datos: bytes, tipo: str, metadatos: dict
    ) -> None:
        blob = self.contenedor.get_blob_client(clave)
        blob.upload_blob(
            datos,
            overwrite=True,
            content_settings=ContentSettings(content_type=tipo),
            metadata=metadatos,
        )

    def url(self, clave: str, segundos: int = 3600) -> str:
        sas = generate_blob_sas(
            account_name=self.cuenta,
            container_name=self.contenedor_nombre,
            blob_name=clave,
            account_key=self.clave_cuenta,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=segundos),
        )

        clave_url = quote(clave, safe="/")
        return (
            f"{self.endpoint_publico}/{self.contenedor_nombre}/"
            f"{clave_url}?{sas}"
        )

    def eliminar(self, clave: str) -> None:
        blob = self.contenedor.get_blob_client(clave)
        try:
            blob.delete_blob()
        except ResourceNotFoundError:
            pass