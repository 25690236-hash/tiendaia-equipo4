# tiendaia-equipo4
Equipo: B primero Equipo: A Pruebas ejecutadas y verificadas

## Despliegue en Render (Laboratorio 5 - Parte B)

* *Cliente web (Static Site):* https://tiendaia-web-equipo4.onrender.com
* *Servicio de IA (Web Service):* https://tiendaia-ia-equipo4.onrender.com

## Reparto de roles (Laboratorio 5)

| Integrante | Rol | Partes y archivos |
| :--- | :--- | :--- |
| *A* | Cómputo y orquestación | Parte A (scripts/bench_entrenamiento.py) y Parte D (k8s/, clúster kind); investiga AWS en la Parte F |
| *B* | Plataforma e IaC | Partes B y C (servicios de Render, render.yaml); investiga Azure |
| *C* | Perímetro y pruebas | Parte E (perimetro/nginx.conf, docker-compose.yml, scripts/prueba_limite.py), carga y tabla de la Parte D (scripts/carga_k8s.py); investiga Google Cloud |

## Parte C: Infraestructura como Código (Render Blueprint)

### 1. Declaración en render.yaml
Se definieron ambos servicios (tiendaia-ia-equipo4 como Web Service de Python y tiendaia-web-equipo4 como Static Site) en el archivo render.yaml en la raíz del repositorio, incluyendo las cabeceras de seguridad (X-Frame-Options: DENY, X-Content-Type-Options: nosniff y Referrer-Policy: no-referrer) para el frontend.

### 2. Uso de sync: false en VENTAS_URL
La variable VENTAS_URL se configuró con sync: false para que Render solicite su valor por entorno sin almacenarlo en el repositorio. Esto evita exponer URLs temporales de GitHub Codespaces o credenciales sensibles en el historial de Git.

### 3. Experimento de deriva de configuración
Al agregar manualmente la variable PRUEBA_DERIVA = 123 desde el panel de Render en tiendaia-ia-equipo4 y ejecutar un *Manual sync* desde el Blueprint, Render reportó "Resources already up to date" y conservó la variable manual. Esto demuestra que Render sincroniza los cambios provenientes de render.yaml respecto a Git, pero no elimina variables adicionales agregadas fuera del archivo declarativo.