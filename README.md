# PLANTILLA PROYECTO - SEMANA 01
Esta plantilla contiene la estructura básica para comenzar los video-series de la semana 1 de "introeucción al desarrollo de videojuegos con ECS"
# CONTINUACIÓN PROYECTO - SEMANA 02

# CONTINUACIÓN PROYECTO - SEMANA 03
Sprites y animaciones (CSurface con `area`, CAnimation), nuevo enemigo Hunter (persigue al jugador y regresa a su origen) y explosiones como entidades independientes.

# CONTINUACIÓN PROYECTO - SEMANA 04
Título y textos (`interface.json`), pausa con P, efectos de sonido y patrón Service Locator para todos los recursos externos (`src/engine/service_locator.py` y `src/engine/services/`).

Característica única: escudo con ESPACIO. Dura 2 s, destruye a los enemigos que toca y se recarga en 5 s (`shield.json`). Incluye anillo animado, sacudida de cámara, parpadeo antes de terminar, barra de recarga con temporizador y sonido al quedar listo.

`esper/` está incluido en el proyecto para que el build web lo encuentre. `thruster.ogg` y `shield_ready.ogg` son sonidos sintetizados para este proyecto.

Build web: `python -m pygbag --build --archive .` genera `build/web.zip`.
