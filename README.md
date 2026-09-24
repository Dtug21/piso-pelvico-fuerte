# Piso Pélvico Fuerte

App web para entrenar el piso pélvico masculino, con la meta de mejorar la firmeza de la erección y el control de la eyaculación. Se usa en el celular y se instala en la pantalla de inicio como una app.

## Qué hace

- **Evaluación inicial**: 7 pruebas de fuerza, el cuestionario IIEF-5 y 2 preguntas de control de eyaculación. Con eso asigna un nivel del 1 al 5.
- **Sesiones guiadas**: temporizador con anillo, pitidos y figuras que muestran cada ejercicio. De 1 a 3 sesiones al día según el nivel.
- **Rutinas de abdomen** que suben de dificultad junto con el nivel.
- **Progresión**: sube o baja de nivel según cómo se sienten las sesiones, y pide reevaluar cada 14 días.
- **Pantalla Hoy**: lo que falta del día, la semana, la evolución de las evaluaciones y un consejo diario.
- **Funciona sin internet** después de abrirla una vez.

Los datos quedan guardados solo en el navegador del teléfono. No hay servidor ni cuentas.

## Instalar en iPhone

1. Abre el link de la app en **Safari**.
2. Toca **Compartir** → **Agregar a pantalla de inicio**.
3. Ábrela desde el ícono: se ve a pantalla completa, como una app.

## Evidencia

Basada en Dorey et al. 2005 (BJU Int), Pastore et al. 2014 (Ther Adv Urol), Rosen et al. 1999 (IIEF-5), Gerbild et al. 2018 (Sex Med), Esposito et al. 2004 (JAMA) y Sapsford et al. 2001. La autoevaluación es orientativa y no reemplaza a un kinesiólogo de piso pélvico ni una consulta médica.

## Estructura

- `index.html`: toda la app (HTML, CSS y JavaScript, sin dependencias).
- `manifest.webmanifest`: nombre, ícono y modo pantalla completa.
- `sw.js`: guarda la app para usarla sin internet. Al cambiar archivos, sube `VERSION`.
- `icons/`: íconos de la app.
