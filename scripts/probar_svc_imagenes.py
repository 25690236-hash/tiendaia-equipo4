import os
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT", "http://seaweedfs:8333"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name="us-east-1"
)

bucket_propio = "tiendaia-imagenes"
bucket_ajeno = "tiendaia-respaldos"

print("1. Subir archivo al bucket propio:")
s3.put_object(Bucket=bucket_propio, Key="prueba.txt", Body=b"Prueba S3")
print("PERMITIDO")

print("\n2. Descargar archivo del bucket propio:")
respuesta = s3.get_object(Bucket=bucket_propio, Key="prueba.txt")
print(respuesta["Body"].read().decode())

print("\n3. Eliminar archivo del bucket propio:")
s3.delete_object(Bucket=bucket_propio, Key="prueba.txt")
print("PERMITIDO")

print("\n4. Escribir en bucket de respaldos:")
try:
    s3.put_object(Bucket=bucket_ajeno, Key="prueba.txt", Body=b"Prueba")
    print("ERROR: operación no debería estar permitida")
except ClientError as e:
    print("DENEGADO:", e.response["Error"]["Code"])

print("\n5. Crear un bucket:")
try:
    s3.create_bucket(Bucket="bucket-no-autorizado")
    print("ERROR: operación no debería estar permitida")
except ClientError as e:
    print("DENEGADO:", e.response["Error"]["Code"])

print("\n6. Buckets visibles:")
for bucket in s3.list_buckets()["Buckets"]:
    print(bucket["Name"])
