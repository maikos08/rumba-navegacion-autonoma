# Cómo está organizado el código

La idea es que se pueda leer de arriba abajo sin saltar entre muchos archivos.

```
proyecto-rumba/
├── config.env              Todos los números ajustables
├── rumba/                  Código que comparten los scripts
│   ├── config.py             lee config.env
│   ├── robot.py              Robot (conexión), Odometria y Rastro
│   ├── servidor.py           el ÚNICO servidor HTTP
│   ├── ejecutar.py           arranque + bucle principal
│   ├── geometria.py          normalizar, limitar, girar_hacia
│   ├── navegacion.py         Navegador (elige el modo) y TareaObjetivo ("ir a un punto")
│   ├── exploracion.py        TareaExploracion (+ exploracion.html): modos sin objetivo
│   ├── modos/                un archivo por modo de navegación
│   │   ├── base.py             lo común: ir al objetivo y seguir una pared
│   │   ├── directo.py          ir a un punto, sin sensores
│   │   ├── parar.py            ir a un punto, parando ante obstáculos
│   │   ├── bug2.py             ir a un punto, rodeando obstáculos
│   │   ├── limpieza.py         recorrer la habitación al azar
│   │   └── seguir_pared.py     explorar siguiendo paredes
│   └── static/               mapa.js y base.css de las páginas web
├── teleoperacion/          main.py + ui.html + README.md
├── navegacion/             main.py + ui.html + README.md
├── evitar_obstaculos/      main.py + ui.html + README.md
├── circuito/               main.py + ui.html + README.md
├── limpieza/               main.py + README.md   (página: rumba/exploracion.html)
├── seguir_pared/           main.py + README.md   (página: rumba/exploracion.html)
└── primeros_scripts/       pruebas de hardware
```

Cada script (`<carpeta>/main.py`) es corto y lo repetido está en `rumba/`. `circuito/` es un script
con su propia página y lógica (la cola de instrucciones) que nadie más usa, por eso no está en `rumba/`.

## Qué pasa en cada ciclo (cada 50 ms)

`rumba/ejecutar.py` repite:

```
1. robot.leer()            sensores + encoders
2. odometria.actualizar()  nueva pose (x, y, θ)
3. tarea.paso(m)           la tarea decide (vr, vl): velocidades de rueda
4. robot.mover(vr, vl)
```

`m` lleva la pose, los sensores y la hora. Mientras tanto, otro hilo atiende el navegador:
`rumba/servidor.py` llama a `tarea.estado_web()` (lo que se dibuja) y a `tarea.acciones_web()` (botones).
Un `lock` evita que ambos hilos toquen los datos a la vez.

## Una tarea

Una clase que hereda de `Tarea` (`rumba/ejecutar.py`) y define:

| Método | Para qué |
|---|---|
| `paso(m)` | Devuelve `(vr, vl)` en mm/s, o `None` para terminar. |
| `estado_web(args)` | Diccionario que se envía a la página. |
| `acciones_web()` | `{"/ruta": función}` con lo que hace cada botón. |
| `linea_consola(m)` | Texto de la consola. |
| `pagina` | Ruta del `ui.html`. |

Para crear una tarea nueva: copia la carpeta más parecida, cambia la clase y el `ui.html`, y listo.

## Los modos

Cada modo es una clase en `rumba/modos/` que hereda de `Modo` (`base.py`, con lo común: ir al objetivo
girando y avanzando, frenado por IR y seguimiento de pared). El `Navegador` (`rumba/navegacion.py`) elige el
modo por su nombre.

| Modo | Archivo | Objetivo | Quién lo usa |
|---|---|---|---|
| `directo` | `directo.py` | sí | `navegacion` |
| `parar` | `parar.py` | sí | `evitar_obstaculos`, `circuito` |
| `bug2` | `bug2.py` | sí | `evitar_obstaculos`, `circuito` |
| `limpieza` | `limpieza.py` | no | `limpieza` |
| `seguir_pared` | `seguir_pared.py` | no | `seguir_pared` |

Los modos con objetivo los usa `TareaObjetivo` (el objetivo se da en la web) y los que no lo tienen,
`TareaExploracion` (botones Iniciar / Parar). `bug2` y `seguir_pared` comparten `seguir_contorno` y la maniobra
de choque, ambas en `base.py`.

Para añadir un modo: crea su archivo con `iniciar(ahora)` y `paso(nav, m, objetivo, inicio)` y regístralo en
`rumba/modos/__init__.py`.

## Principios aplicados (sin pasarse)

* **Una responsabilidad por archivo:** `robot.py` habla con el robot, `servidor.py` con el navegador,
  `navegacion.py` decide cómo ir a un punto, `config.py` lee los parámetros.
* **Un solo servidor HTTP** y **un solo sitio** para odometría, bucle y navegación: nada repetido entre scripts.
* **Sin números mágicos:** todo sale de `config.env`.
* **Dependencias por parámetro:** las tareas reciben `cfg` y `Robot` acepta una fábrica en lugar de `Create2`,
  por si se quiere probar con un robot simulado.

## Cambios respecto al código original

* `IR_PARADA` / `IR_LIBRE`: `evitar_obstaculo.py` usaba 40 / 20 y `caminito.py` 50 / 30. Ahora hay un único
  valor (50 / 30, el más reciente) en `config.env`.
* Las cuatro páginas comparten el estilo de mapa de `circuito`.
* Una petición HTTP con argumentos inválidos devuelve 400 (antes podía cortar la conexión).
* La teleoperación envía la orden a las ruedas después de leer los sensores y no antes (50 ms de diferencia).

Todo lo demás se comprobó idéntico al código original con un robot simulado.
