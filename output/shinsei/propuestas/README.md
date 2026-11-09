# Piezas puntuales · Shinsei Store

Estas piezas se entregan fuera de `public/`. No están alojadas ni enlazadas en el sitio.

## Instagram: tres cuadrados sin QR

Archivos finales de 1080 × 1080 en `../final/`:

1. `instagram-01-aurora.png`: este jueves en Shinsei, fecha de inicio, 5 p. m., dirección y excepciones de diciembre.
2. `instagram-02-oscilio.png`: Silver Age, mazos accesibles, preconstruidos y premios de Omens of the Third Age.
3. `instagram-03-zyggy.png`: Mesa Inicial, enseñanza y préstamo de mazos con aviso previo.

Cada pieza tiene un héroe protagonista a fondo completo, sin paneles claros; el lila claro se usa solo en acentos de texto. La información se reparte en las tres y pueden usarse como carrusel o como tres posts consecutivos. El texto complementario está en `instagram-caption.txt`.

## Afiche permanente

`../final/afiche-tienda-a3.pdf`: una página A3, sin fechas concretas. Puede imprimirse a A4 ajustando a página. Vista PNG: `../final/afiche-tienda.png`.

Conserva el collage de los tres héroes, logos, preconstruidos, set de premios, horario semanal y dirección. El QR solo se usa en este afiche y dirige a Mesa Inicial para coordinar enseñanza y préstamo de mazos con anticipación.

## Fuentes

`generate_launch.py` y `mesa-inicial-qr.png`. Los originales de las imágenes están en `../materiales/`. Ejecutar `python output/shinsei/propuestas/generate_launch.py` para generar los HTML autónomos con tipografía e imágenes incrustadas. Los HTML intermedios y las exploraciones anteriores son archivos locales, no incluidos en el PR.

La fuente es Albert Sans, desde `/usr/share/fonts/TTF/AlbertSans[wght].ttf`. Exportar los tres HTML de Instagram en Chromium a 1080 × 1080. Para el PDF, imprimir `afiche-tienda.html` en A3, con gráficos de fondo activados y encabezados/pies del navegador desactivados. El CSS incluye el formato de impresión.

Resumen del sitio y validación: `docs/lanzamiento-shinsei.md`.
