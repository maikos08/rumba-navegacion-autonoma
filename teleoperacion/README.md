# Teleoperación con odometría

Conduces el robot desde el navegador y ves en tiempo real su posición estimada por odometría
(ver [docs/odometria.md](../docs/odometria.md)). Es la herramienta para comprobar que la odometría y
las ruedas funcionan antes de lanzar tareas autónomas, y para calibrarla.

## Ejecutar

```bat
conda activate create2
python teleoperacion\main.py
```

Se abre `http://127.0.0.1:8000` con el mapa. Pon el robot en el suelo: **el origen (0, 0, 0°) es
donde arranca**.

## Controles

| Tecla | Botón | Acción | Velocidades (`config.env`) |
|---|---|---|---|
| `W` | ▲ W | Avanzar | `V_AVANCE` (150 mm/s) |
| `A` | ◀ A | Girar a la izquierda sobre sí mismo | `V_GIRO` (100 mm/s por rueda) |
| `D` | D ▶ | Girar a la derecha sobre sí mismo | `V_GIRO` |
| `Espacio` | Parar | Detener | — |
| `Q` | Salir | Parar el robot y cerrar el programa | — |

También se puede parar con `Ctrl+C` en la consola, que además imprime `x`, `y` y `θ` en mm.

## Qué se ve

* Cabecera: `x`, `y` (mm) y `θ` (grados, normalizado a ±180°).
* Mapa: cuadrícula cada 0,5 m, rastro azul, punto verde de origen y el robot (círculo rojo, Ø 348 mm)
  con una línea que indica hacia dónde mira.

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Clase `Teleoperacion`: traduce teclas en velocidades de rueda. |
| `ui.html` | Interfaz (usa `rumba/static/mapa.js`). |

## Mejoras propuestas

1. **Parada de seguridad (watchdog).** Hoy, si cierras la pestaña o se cae la conexión, el robot
   **sigue ejecutando la última orden**. Convendría que `W/A/D` solo muevan mientras la tecla esté
   pulsada (o parar si no llegan órdenes en ~500 ms).
2. **Velocidad ajustable** con un deslizador o con `+`/`-`, y giro suave (arco) combinando teclas.
3. **Exportar el recorrido** a CSV para analizar la deriva de la odometría fuera del programa.
4. **Asistente de calibración**: pedir "avanza 1 m", comparar con la medida real y proponer nuevos
   valores de `DIAMETRO_RUEDA` y `B` (ver [docs/odometria.md](../docs/odometria.md)).
5. **Mostrar sensores** (light bumpers, parachoques, batería) como en `circuito`.
