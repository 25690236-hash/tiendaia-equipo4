# Ejercicio 18. Responsabilidad compartida de TiendaIA

## 1. Componentes del proyecto

TiendaIA está desarrollado mediante una arquitectura de microservicios, utilizando contenedores Docker y Kubernetes para ejecutar y administrar algunos de sus servicios.

Los principales componentes del proyecto son:

| Componente | Función |
|---|---|
| GitHub | Almacena el código fuente y permite controlar las versiones del proyecto. |
| GitHub Codespaces | Entorno de desarrollo en la nube donde trabajamos con el proyecto. |
| Docker | Permite crear y ejecutar contenedores. |
| Docker Compose | Administra los diferentes servicios y sus conexiones. |
| Kubernetes (Kind) | Orquesta los contenedores y administra los despliegues. |
| Servicio IA | Realiza predicciones utilizando un modelo de aprendizaje automático. |
| Gateway | Recibe y dirige las solicitudes hacia los microservicios. |
| Clientes | Administra la información de los clientes. |
| Productos | Administra el catálogo de productos. |
| Ventas | Registra y administra las ventas. |
| Notificaciones | Gestiona las notificaciones del sistema. |
| Worker | Ejecuta tareas de procesamiento en segundo plano. |
| IA Listener | Escucha y procesa mensajes relacionados con el servicio de IA. |
| MySQL | Base de datos relacional. |
| MongoDB | Base de datos NoSQL. |
| Redis | Almacena información en memoria. |
| RabbitMQ | Gestiona la comunicación mediante mensajes entre servicios. |
| Nginx | Proporciona el servidor web para el cliente. |
| Deployment | Mantiene las réplicas del servicio IA en Kubernetes. |
| Service | Permite la comunicación con el servicio IA dentro del clúster. |
| HPA | Ajusta automáticamente las réplicas del servicio IA según el uso de CPU. |

## 2. Responsabilidad compartida

En TiendaIA, la seguridad es una responsabilidad compartida entre los proveedores de servicios tecnológicos y nuestro equipo de desarrollo. Los proveedores protegen la infraestructura que ofrecen, mientras que nosotros debemos configurar correctamente los servicios, proteger los datos y controlar los accesos.

### Tabla de responsabilidades

| Componente | ¿Qué asegura el proveedor? | ¿Qué nos toca asegurar? |
|---|---|---|
| GitHub | Infraestructura de la plataforma y disponibilidad del servicio. | Proteger el repositorio, controlar permisos y evitar publicar contraseñas o tokens. |
| GitHub Codespaces | Infraestructura de las máquinas virtuales y funcionamiento del entorno. | Proteger el acceso, configurar el entorno y cuidar las credenciales. |
| Docker | Herramientas para crear y ejecutar contenedores. | Utilizar imágenes confiables y configurar correctamente los contenedores. |
| Docker Compose | Herramienta para administrar servicios y redes. | Configurar puertos, redes, volúmenes y variables de entorno de forma segura. |
| Kubernetes (Kind) | Kubernetes proporciona los mecanismos de orquestación; Kind facilita su ejecución local. | Configurar permisos, despliegues, servicios y políticas de seguridad. |
| Servicio IA | Infraestructura de ejecución proporcionada por la plataforma donde se despliega. | Proteger el modelo, las rutas de la API y los datos procesados. |
| Gateway | No contamos con un proveedor externo específico para este componente. | Controlar las solicitudes, validar entradas y proteger los endpoints. |
| Clientes | No contamos con un proveedor externo específico para este microservicio. | Validar y proteger la información de los clientes. |
| Productos | No contamos con un proveedor externo específico para este microservicio. | Validar los datos y controlar las operaciones sobre productos. |
| Ventas | No contamos con un proveedor externo específico para este microservicio. | Proteger los registros y validar las operaciones de venta. |
| Notificaciones | No contamos con un proveedor externo específico para este microservicio. | Controlar el envío y proteger la información de las notificaciones. |
| Worker e IA Listener | No contamos con un proveedor externo específico para estos servicios. | Controlar los procesos y validar los mensajes recibidos. |
| MySQL | El proyecto utiliza una imagen de base de datos; no hay un proveedor administrado identificado. | Proteger los datos, usuarios, contraseñas y respaldos. |
| MongoDB | El proyecto utiliza una imagen de base de datos; no hay un proveedor administrado identificado. | Configurar autenticación y proteger la información almacenada. |
| Redis | El proyecto utiliza una imagen de Redis. | Proteger el acceso y evitar conexiones no autorizadas. |
| RabbitMQ | El proyecto utiliza una imagen de RabbitMQ. | Proteger las credenciales, colas y permisos de acceso. |
| Nginx | Se utiliza una imagen de Nginx. | Configurar correctamente el servidor web y proteger las conexiones. |

## 3. Pendientes de seguridad

Después de revisar la arquitectura de TiendaIA y las configuraciones disponibles, identificamos las siguientes medidas de seguridad que necesitan implementarse o verificarse.

Los elementos marcados en rojo representan pendientes de seguridad:

- <span style="color:red">**Control de acceso:** implementar autenticación y autorización para evitar que usuarios no autorizados accedan a los servicios.</span>
- <span style="color:red">**Protección de credenciales:** verificar que las contraseñas, tokens y claves no estén expuestos en el código o repositorio.</span>
- <span style="color:red">**Protección de puertos:** comprobar que solamente estén publicados los puertos necesarios y que los servicios internos no sean accesibles desde Internet.</span>
- <span style="color:red">**Segmentación de redes:** verificar que las bases de datos, RabbitMQ y los microservicios estén aislados de la red pública.</span>
- <span style="color:red">**Límite de peticiones (Rate Limiting):** implementar y comprobar límites para evitar solicitudes excesivas al sistema.</span>
- <span style="color:red">**HTTPS y cifrado:** configurar conexiones seguras para proteger la información transmitida.</span>
- <span style="color:red">**Protección de bases de datos:** verificar autenticación, permisos y respaldos de MySQL, MongoDB y Redis.</span>
- <span style="color:red">**Cabeceras de seguridad:** comprobar que el servidor web utilice cabeceras para reducir riesgos como clickjacking y ataques relacionados con tipos de contenido.</span>
- <span style="color:red">**Monitoreo y registros:** fortalecer la supervisión de los servicios y revisar los registros para detectar actividades sospechosas.</span>

## 4. Relación de pendientes con principios de seguridad

Cada pendiente identificado se relaciona con uno o varios principios de seguridad que ayudan a proteger TiendaIA.

| Pendiente de seguridad | Principio relacionado | Justificación |
|---|---|---|
| Control de acceso | Mínimo privilegio | Cada usuario debe tener únicamente los permisos necesarios. |
| Protección de credenciales | Confidencialidad | Evita que personas no autorizadas obtengan información sensible. |
| Protección de puertos | Defensa en profundidad | Reduce los puntos de entrada que podrían aprovechar los atacantes. |
| Segmentación de redes | Defensa en profundidad | Aísla los servicios y limita el impacto de un posible ataque. |
| Límite de peticiones | Disponibilidad | Evita el abuso de solicitudes que puede afectar el funcionamiento del sistema. |
| HTTPS y cifrado | Confidencialidad e integridad | Protege la información durante su transmisión. |
| Protección de bases de datos | Mínimo privilegio y confidencialidad | Limita el acceso a los datos y protege la información almacenada. |
| Cabeceras de seguridad | Defensa en profundidad | Agrega medidas adicionales de protección al servidor web. |
| Monitoreo y registros | Detección y respuesta | Permite identificar comportamientos sospechosos y atender incidentes. |

### Conclusión

La seguridad de TiendaIA depende tanto de los proveedores de infraestructura como de nuestro equipo de desarrollo. Aunque contamos con herramientas como Docker, Kubernetes y GitHub, debemos configurar correctamente los servicios y aplicar medidas de protección.

Esta actividad nos permite identificar los aspectos que todavía necesitan atención y establecer una lista de trabajo para mejorar la seguridad del proyecto durante el Hito 4.