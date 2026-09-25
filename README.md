# Piso Pélvico Fuerte

App web para entrenar el piso pélvico, para hombres y mujeres. Se adapta a lo que cada persona quiere mejorar: erección, control de la eyaculación, escapes de orina, urgencia, goteo, recuperación de próstata, prolapso, vida sexual, dolor pélvico, embarazo y posparto. Se usa en el celular y se instala en la pantalla de inicio como una app.

## Qué hace

- **Perfil y objetivos**: hombre o mujer, qué quiere mejorar y, en mujeres, embarazo o posparto.
- **Evaluación**: 7 pruebas de fuerza y los cuestionarios validados de cada objetivo (IIEF-5, ICIQ-UI SF, FSFI-6, síntomas de prolapso, urgencia, dolor). Asigna un nivel del 1 al 5, o un plan de relajación si el músculo está tenso de más.
- **Plan según objetivos**: contracciones rápidas extra, apretar y toser, frenar la urgencia, posiciones seguras en embarazo y rutinas de abdomen adaptadas.
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

Basada en Dumoulin et al. 2018 y Woodley et al. 2020 (Cochrane), Hagen et al. 2014 (Lancet), Burgio et al. 1998 (JAMA), Anderson et al. 2015 (Cochrane), Dorey et al. 2005 (BJU Int), Pastore et al. 2014, Avery et al. 2004 (ICIQ-UI SF), Isidori et al. 2010 (FSFI-6), Rosen et al. 1999 (IIEF-5) y Sapsford et al. 2001. La autoevaluación es orientativa y no reemplaza a un kinesiólogo de piso pélvico ni una consulta médica.

## Estructura

- `index.html`: toda la app (HTML, CSS y JavaScript, sin dependencias).
- `manifest.webmanifest`: nombre, ícono y modo pantalla completa.
- `sw.js`: guarda la app para usarla sin internet. Al cambiar archivos, sube `VERSION`.
- `icons/`: íconos de la app.
