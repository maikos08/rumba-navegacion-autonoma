# Primeros scripts (pruebas de hardware)

Scripts pequeños para comprobar el robot antes de usar las tareas. No usan el servidor web.
El puerto serie se lee de [`config.env`](../config.env) (`PUERTO`).

| Script | Para qué |
|---|---|
| `arreglar_get_sensors.py` | **Una vez por entorno.** Reescribe `get_sensors()` de `pycreate2` (indentación rota, mensajes de reinicio del robot). Ver [docs/anaconda.md](../docs/anaconda.md). |
| `test_movimiento.py` | Adelante 2 s, giro 2 s, atrás 2 s a 100 mm/s. Comprueba motores y cable. **Deja espacio libre.** |
| `test_sensores.py` | 5 minutos imprimiendo los 6 light bumpers y la batería cada 0,5 s. Sirve para ver qué valores dan tus obstáculos y ajustar `IR_*`. |
| `test_sensores_diag.py` | Igual, pero si `get_sensors()` falla muestra los bytes pendientes, reintenta y cuenta los fallos. Para diagnosticar cortes de comunicación. |

## Ejecutar

```bat
conda activate create2
python primeros_scripts\test_movimiento.py
```

`Ctrl+C` detiene el script y para el robot.

## Orden recomendado

1. `arreglar_get_sensors.py` (solo la primera vez).
2. `test_sensores.py` — ¿responde el robot?
3. `test_movimiento.py` — ¿se mueve como esperas?
4. [`teleoperacion`](../teleoperacion/README.md) — ¿la odometría cuadra con lo que mides?

## Mejoras propuestas

* Unificar `test_sensores.py` y `test_sensores_diag.py` en un único script con opción `--diagnostico`.
* Aceptar `--puerto` y `--velocidad` por línea de comandos.
* Reutilizar `rumba.robot.Robot` en lugar de `pycreate2` directamente (hoy usan la librería sin pasar
  por el reintento de lectura).
