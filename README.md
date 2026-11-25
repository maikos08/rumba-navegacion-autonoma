# Proyecto Rumba — Robots Autónomos con iRobot Create 2

Navegación de un **iRobot Create 2** (Roomba) con odometría propia, evitación de obstáculos y una
interfaz web para controlarlo. Proyecto de la asignatura *Robots Autónomos* del Máster en Sistemas
Inteligentes (Universidad de Salamanca).

Todo funciona con Python estándar más `pycreate2`; la interfaz es una página web local (sin frameworks).

## Scripts

| Carpeta | Tarea | Qué hace | Ejecutar |
|---|---|---|---|
| [`teleoperacion/`](teleoperacion/README.md) | Odometría | Conduces con el teclado y ves la posición estimada | `python teleoperacion\main.py` |
| [`navegacion/`](navegacion/README.md) | **Ejecución de un movimiento planificado** | Giro + avance hasta una posición | `python navegacion\main.py` |
| [`evitar_obstaculos/`](evitar_obstaculos/README.md) | Evitación de colisiones | Ir a un punto parando o rodeando con **Bug2** | `python evitar_obstaculos\main.py` |
| [`circuito/`](circuito/README.md) | Planificación sencilla | Cola de "Ir a" y "Girar", con repetición | `python circuito\main.py` |
| [`limpieza/`](limpieza/README.md) | **Limpieza de una habitación** (*chocayvuelve*) | Recorre la habitación esquivando obstáculos con giros al azar y sin atascarse | `python limpieza\main.py` |
| [`seguir_pared/`](seguir_pared/README.md) | **Exploración reactiva** (*seguirpared*) | Busca una pared y la sigue | `python seguir_pared\main.py` |
| [`primeros_scripts/`](primeros_scripts/README.md) | Pruebas de hardware | Sensores, motores y parche de `pycreate2` | `python primeros_scripts\test_sensores.py` |

Cada carpeta tiene su propio README con los controles, el funcionamiento y mejoras propuestas. El código compartido está en [`rumba/`](rumba) (ver [docs/arquitectura.md](docs/arquitectura.md)).

## Inicio rápido

1. Instala Anaconda y crea el entorno ([docs/anaconda.md](docs/anaconda.md)):

   ```bat
   conda env create -f environment.yml
   conda activate create2
   python primeros_scripts\arreglar_get_sensors.py
   ```
2. Conecta el robot por USB y escribe su puerto (`COMx`) en [`config.env`](config.env).
3. Pon el robot en el suelo, con espacio libre, y lanza un script, por ejemplo:

   ```bat
   python teleoperacion\main.py
   ```

   Se abre `http://127.0.0.1:8000`. Con `Ctrl+C` en la consola o el botón *Salir* se para el robot.

**¿Sin Anaconda?** No hace falta. Basta con Python 3.10 o superior y `pycreate2` (el resto es biblioteca estándar):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python primeros_scripts\arreglar_get_sensors.py
```

(En Linux/macOS: `source .venv/bin/activate`.) Después se usa igual que arriba. Más detalles en
[docs/anaconda.md](docs/anaconda.md).

Los comandos son los de **Windows**. En Linux o macOS basta con cambiar `\` por `/` y el puerto por algo como
`/dev/ttyUSB0`.

## Sistema de referencia

El origen (0, 0) y θ = 0° están **donde arranca el robot**, con **x hacia delante** e **y hacia la
izquierda**; giros positivos hacia la izquierda (antihorario). Distancias en mm internamente y en metros en
las páginas. Cada vez que se reinicia el script, el origen se pierde (la odometría no tiene memoria).

## Configuración

Todos los números ajustables (puerto, velocidades, umbrales de los sensores, parámetros de Bug2...)
están en [`config.env`](config.env), con comentarios y unidades. Cualquier clave se puede sobrescribir
sin editar el archivo:

```bat
set RUMBA_PUERTO=COM7
set RUMBA_V_AVANCE=100
python navegacion\main.py
```

## Documentación

| Documento | Contenido |
|---|---|
| [docs/anaconda.md](docs/anaconda.md) | Entorno de conda, parche de `pycreate2`, puerto serie, problemas habituales |
| [docs/odometria.md](docs/odometria.md) | Cómo se calcula la posición, fórmulas, errores y calibración |
| [docs/arquitectura.md](docs/arquitectura.md) | Cómo está organizado el código y cómo añadir una tarea |

## Seguridad

* Prueba siempre en una zona despejada y con el robot a la vista; `Ctrl+C` o *Salir* lo detienen.
* La web solo escucha en `127.0.0.1` y no tiene autenticación: no la expongas a la red.
* `teleoperacion` no tiene parada automática si se pierde la conexión (ver sus mejoras propuestas).


## Licencia

Sin licencia definida todavía: añade un archivo `LICENSE` (por ejemplo MIT) antes de publicar si quieres
que otros puedan reutilizar el código.
