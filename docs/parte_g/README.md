# Parte G: salud de los servicios

`docker-compose.yml` define un healthcheck HTTP común para los cinco servicios
Python. Las dependencias de `ventas`, `ia` y `gateway` esperan a que los
servicios Python requeridos estén `healthy`; Ventas solo espera a que Redis esté
iniciado (`service_started`), como indica la práctica.

## Evidencias pendientes de capturar

1. Con todos los servicios en marcha: `docker compose ps` mostrando los
   healthchecks en estado `healthy`.
2. Después de `docker compose stop redis`, esperar 60 segundos y capturar
   `docker compose ps ventas` en estado `unhealthy`.
3. Tras `docker compose start redis`, registrar cuánto tarda Ventas en volver a
   `healthy` y capturar el resultado.

Todavía faltan las capturas de pantalla exigidas por la rúbrica; los resultados
de la ejecución local se registran abajo.

## Resultados observados

- Con todos los servicios activos, los cinco servicios Python aparecieron como
  `healthy`; MySQL y MongoDB también estaban `healthy`. Redis se mostró `Up`
  (esta práctica no le configura healthcheck) y web se mostró `Up`.
- Después de detener Redis y esperar al menos 60 segundos, `docker compose ps
  ventas` mostró `Up ... (unhealthy)`. `docker inspect` mostró el healthcheck
  fallando por superar el timeout de 3 segundos.
- Después de `docker compose start redis`, Ventas regresó a `healthy` en unos
  6 segundos.

Guarda las capturas de los estados `healthy`, `unhealthy` y de la recuperación
en esta carpeta para completar la evidencia visual de la rúbrica.

## Análisis para el reporte

`Up` indica que el proceso principal del contenedor sigue ejecutándose.
`healthy` indica que, además, una comprobación funcional reciente terminó bien.
Por eso un contenedor puede estar `Up` y `unhealthy`: por ejemplo, Ventas sigue
ejecutándose pero su endpoint `/health` falla al hacer `PING` a Redis. Docker
usa el estado de salud para ordenar el arranque de dependencias; el healthcheck
por sí solo no reinicia un proceso que continúa activo.
