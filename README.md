# tiendaia-equipo4
Equipo: B primero Equipo: A Pruebas ejecutadas y verificadas

## 11. Parte F. Investigación documental: servicios en la nube por proveedor

### 11.2. F.2 Tabla de servicios

| Categoría | Modelo | AWS | Azure | Google Cloud | Plataforma Especializada (Vercel) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *Funciones serverless* | FaaS | AWS Lambda | Azure Functions | Cloud Functions | Vercel Functions |
| *Máquinas virtuales* | IaaS | Amazon EC2 | Azure Virtual Machines | Compute Engine | No ofrece |
| *Contenedores gestionados* | CaaS / PaaS | AWS App Runner | Azure Container Apps | Cloud Run | No ofrece |
| *Almacenamiento de objetos* | Storage | Amazon S3 | Azure Blob Storage | Cloud Storage | Vercel Blob |
| *Bases de datos SQL* | DBaaS | Amazon RDS | Azure SQL Database | Cloud SQL | Vercel Postgres |
| *Bases de datos NoSQL* | DBaaS | Amazon DynamoDB | Azure Cosmos DB | Firestore | Vercel KV |
| *Mensajería* | Message Broker | Amazon SQS | Azure Service Bus | Cloud Pub/Sub | No ofrece |
| *Identidad y acceso* | IAM / Auth | AWS IAM / Cognito | Microsoft Entra ID | Cloud IAM | Vercel Auth |

---

### Tabla Anexa: Capa gratuita, Unidad de cobro y Uso en proyectos de IA

| Servicio | Capa Gratuita / Límites | Unidad de Cobro | Uso típico en proyectos de IA |
| :--- | :--- | :--- | :--- |
| *AWS Lambda* | 1M peticiones/mes gratis | Por petición y GB-segundo | API gateways y llamadas a modelos de IA |
| *Amazon EC2* | 750 hrs/mes (t2.micro / t3.micro) por 12 meses | Por hora/segundo según GPU/CPU | Entrenamiento e inferencia de LLMs locales |
| *AWS App Runner* | 2,000 GB-horas gratis el primer mes | Por vCPU/GB por hora | Despliegue de backend FastAPI en contenedor |
| *Amazon S3* | 5 GB almacenamiento por 12 meses | Por GB/mes | Datasets, vectores e imágenes generadas |
| *Amazon RDS* | 750 hrs/mes (db.t2.micro) por 12 meses | Por hora de instancia | Base de datos relacional de la app |
| *Amazon DynamoDB* | 25 GB almacenamiento permanente | Por RCU/WCU o peticiones | Historial de chat y logs no estructurados |
| *Amazon SQS* | 1M peticiones/mes gratis | Por millón de mensajes | Colas asíncronas para tareas pesadas de IA |
| *AWS IAM / Cognito* | 50,000 MAU gratis en Cognito | Por usuarios activos mensuales | Autenticación y control de accesos |
| *Azure Container Apps* | 180k vCPU-s + 2M peticiones/mes | Por vCPU-s y GB-s | Contenedores de microservicios e integradores |
| *Azure Blob Storage* | 5 GB por 12 meses | Por GB/mes | Documentos y archivos para RAG |
| *Google Cloud Run* | 2M peticiones/mes gratis | Por vCPU-s y GB-s | Orquestadores de agentes de IA |
| *Google Firestore* | 1 GB + 50k lecturas diarias | Por operaciones y GB/mes | Base NoSQL para chat en tiempo real |
| *Vercel Functions* | 100 GB-horas + 1M ejecuciones | Por GB-hora y peticiones | Frontend y Serverless APIs |
| *Vercel Postgres / Blob* | 256 MB DB / 1 GB Blob gratis | Por GB de almacenamiento | Datos livianos del proyecto e historial |