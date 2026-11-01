# radioguasa-catalog

Copia de respaldo del catálogo de emisoras de RadioGuasa, para cuando Radio Browser no responde
(por ejemplo, en la primera instalación durante una caída).

Cada día, una tarea de GitHub Actions descarga de Radio Browser las emisoras más escuchadas y que
funcionan de cada país (hasta 500) y las publica como ficheros `docs/XX.json` (código de país),
en el mismo formato que la API. La app los usa solo si Radio Browser falla y esa región aún no
tiene lista guardada.

## Puesta en marcha (una vez)
1. Crear en GitHub un repositorio **público** llamado `radioguasa-catalog` (Pages gratuito exige repositorio público)
   y subir el contenido de esta carpeta, incluida la carpeta oculta `.github`.
2. Settings → Actions → General → *Workflow permissions* → **Read and write permissions** → Save.
3. Settings → Pages → Source: *Deploy from a branch* → rama `main`, carpeta `/docs` → Save.
4. Pestaña Actions → *Actualizar catálogo* → *Run workflow* (la primera vez a mano; tarda unos 3 minutos).
5. Comprobar que existe `https://TU_USUARIO.github.io/radioguasa-catalog/ES.json` (Pages puede tardar 1–2 minutos).
6. En la app: `data/RadioApi.kt` → cambiar `USUARIO` en `SNAPSHOT_USER` por tu usuario de GitHub.
7. (Recomendado) Descargar `docs/seed.json` y copiarlo a `app/src/main/assets/stations_seed.json` para que
   la app lleve una lista inicial de España incluida.
8. Editar `docs/index.html` y sustituir `[CORREO]` por el correo de soporte.

## Notas
- Una petición cada 2 s y solo una vez al día: uso mínimo de Radio Browser.
- Los datos proceden de Radio Browser (radio-browser.info): se cita la fuente en `docs/index.html` y en la app.
- Si Radio Browser está caído cuando corre la tarea, no cambia nada y se conservan los ficheros anteriores.
- GitHub desactiva las tareas programadas de un repositorio tras 60 días sin actividad. Como la tarea hace un
  commit cuando hay cambios, debería mantenerse viva; conviene mirar la pestaña Actions una vez al mes.
- La app prueba primero GitHub Pages y, si falla, el mismo repositorio a través de jsDelivr.
