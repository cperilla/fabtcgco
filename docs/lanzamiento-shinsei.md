# Lanzamiento de Silver Age en Shinsei Store

## Programación confirmada

Período: 12 de noviembre de 2026 a 12 de febrero de 2027.

- Jueves, 5 p. m.: Silver Age en Shinsei Store, Cra. 52B #18-40, Cali. Doce encuentros; no hay actividad el 24 ni el 31 de diciembre.
- Sábados, 3 p. m.: Classic Constructed en Chaos Store. Trece encuentros.
- Martes, 5 p. m.: Free Play en Chaos Store. Se conserva la recurrencia anterior: trece encuentros.
- Sábados, 3 p. m.: Silver Age en Palmira. Se conserva la recurrencia anterior: trece encuentros.
- Living Legend se retira de la nueva programación. No hay eventos especiales confirmados para este período.

Enseñanza y préstamo de mazos en Shinsei se coordinan con anticipación mediante Mesa Inicial. Premios del set **Omens of the Third Age**, según la confirmación del organizador. No se publican cantidades, reparto ni costo de inscripción porque no se han especificado.

## Calendario y sitio

Los eventos siguen almacenados como JSON trimestral en `src/data/Eventos_Comunidad_Q4_2026.json` y `src/data/Eventos_Comunidad_Q1_2027.json`. `src/data/active-calendars.json` selecciona los archivos activos y lo consumen tanto Astro como la herramienta de Challonge. Los archivos históricos conservan sus eventos originales.

Para añadir o actualizar torneos, editar el registro trimestral existente, conservando `TournamentURL` y `TournamentName`. No crear otro registro para el mismo evento. Al cambiar de período, actualizar el manifiesto de archivos activos. Los datos de Shinsei y las rutas de sus imágenes están en `src/data/shinsei.json`.

La portada, calendario, Empezar, Mejorar, Mesa Inicial y páginas de formatos reflejan la nueva programación. `ShinseiAnnouncement.astro` comparte la invitación, ubicación, premios y coordinación previa. Los afiches, imágenes sociales y promocionales de preconstruidos se conservan como entregables puntuales fuera de `public/`; no se muestran ni se ofrecen como descargas en el sitio.

El calendario agrupa por año y mes para cruzar correctamente de 2026 a 2027. Cada evento de Shinsei muestra el logo transparente, dirección y acceso a Mesa Inicial. iCal y Google Calendar incluyen la sede correcta, dirección y zona horaria de Colombia; no se inventa una hora de finalización.

Challonge conserva `--calendar` para elegir un archivo individual y ahora carga por defecto los mismos trimestres que el sitio. Se añadió Shinsei como sede y se conserva la descripción del evento, incluidos premios y coordinación. No se crearon ni actualizaron torneos remotos. La asociación de rankings para Shinsei queda sin configurar hasta que se definan los rankings correspondientes.

## Imágenes revisadas e incorporadas

| Original conservado en `output/shinsei/materiales/` | Uso |
| --- | --- |
| `silver_age_logo.png` | Logo oficial en las piezas e invitación web. |
| `omens_of_the_third_age_logo-720x274.png` | Identificación del set de premios. |
| `OMN_art_sig_aurora_adult-402x560.jpg` | Aurora en el collage. |
| `OMN_art_sig_oscilio_young-402x560.jpg` | Oscilio en el collage. |
| `OMN_art_sig_zyggy_adult-402x560.jpg` | Zyggy en el collage. |
| `slv_tbx_lineup_ch1.png` | Promocional de Dash, Bravo, Iyslander, Kayo y Viserai. |
| `en_slv_prism_aot_tbx_LF-1.png` | Promocional de Prism, Advent of Thrones. |
| `en_slv_viserai_bw_tbx_LF-1.png` | Promocional de Viserai, Between Worlds. |

Los originales se conservan en `output/shinsei/materiales/`. Los tres artes y las imágenes de productos se usan únicamente en los entregables. En `public/images/shinsei/` se mantienen solo los logos de Silver Age y Omens usados por el contenido web. El logo de Shinsei conserva el diseño original y usa transparencia en el negro exterior; está en `public/images/stores/shinsei.png`.

El collage presenta ilustraciones del set; no es una lista de héroes o cartas legales para Silver Age.

## Piezas y fuentes editables

Todos estos entregables están fuera de `public/` y no se despliegan con el sitio.

- Instagram 1: `output/shinsei/final/instagram-01-aurora.png`, 1080 × 1080. Este jueves en Shinsei, horario, dirección, inicio y excepciones de diciembre.
- Instagram 2: `output/shinsei/final/instagram-02-oscilio.png`, 1080 × 1080. Silver Age, mazos accesibles, preconstruidos, comunidad y premios de Omens.
- Instagram 3: `output/shinsei/final/instagram-03-zyggy.png`, 1080 × 1080. Mesa Inicial, enseñanza, préstamo de mazos y coordinación con anticipación.
- Los tres cuadrados tienen un héroe prominente cada uno y no tienen QR. Pueden publicarse como carrusel o como tres posts consecutivos.
- Afiche permanente: `output/shinsei/final/afiche-tienda-a3.pdf`, una página A3 sin fechas concretas. Conserva el collage, horario semanal, dirección, preconstruidos, premios y preparación mediante Mesa Inicial. Puede imprimirse a A4 ajustando a página. Vista PNG: `output/shinsei/final/afiche-tienda.png`, 1080 × 1527.
- Pie de Instagram: `output/shinsei/propuestas/instagram-caption.txt`.

Fuente editable: `output/shinsei/propuestas/generate_launch.py`, con `mesa-inicial-qr.png` para el afiche impreso. Ejecutar `python output/shinsei/propuestas/generate_launch.py` para generar HTML autónomos con tipografía e imágenes incrustadas. Las exportaciones intermedias y las exploraciones anteriores permanecen locales y no se incluyen en el PR.

El generador usa Albert Sans desde `/usr/share/fonts/TTF/AlbertSans[wght].ttf`; si se cambia de entorno, ajustar esa ruta. Exportar los tres HTML de Instagram en Chromium a 1080 × 1080. Para el PDF, imprimir `afiche-tienda.html` en A3, con gráficos de fondo activados y encabezados/pies del navegador desactivados; el CSS define tamaño y márgenes. El QR del afiche apunta a `https://fabtcgcolombia.club/mesa-inicial`, con el enlace existente de WhatsApp.

No se añadieron dependencias del sitio ni generación de imágenes mediante IA.

## Validación

- PDF comprobado con `pdfinfo` y renderizado: una página A3, texto sin fechas concretas y sin recortes.
- `yarn build`: 54 páginas compiladas.
- `TZ=America/Bogota node tests/shinsei-launch.test.mjs`: cuatro pruebas de recurrencias, excepciones, fechas locales y exportaciones.
- Chromium a 390 y 1366 px: ocho páginas revisadas, sin desbordamiento horizontal ni imágenes nuevas rotas. Se comprobaron los cuatro meses en orden, 51 eventos y 12 identificaciones de Shinsei.
- Capturas locales de portada, calendario y Mesa Inicial: `output/shinsei/web/` (evidencia local, no incluida en el PR).

Los cambios están en el repositorio local; no se ejecutó despliegue a Cloudflare.
