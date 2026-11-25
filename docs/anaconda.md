# Entorno de Python con Anaconda

El proyecto usa un entorno de conda llamado **`create2`** con Python 3.10 y una única dependencia
externa, [`pycreate2`](https://pypi.org/project/pycreate2/) 0.8.0 (que instala `pyserial`,
`colorama` y `simplejson`). Todo lo demás es biblioteca estándar.

> Todos los comandos se escriben en **Anaconda Prompt** (menú Inicio → "Anaconda Prompt").
> Funcionan igual en CMD y, tras `conda init powershell`, en PowerShell.

> **Anaconda no es obligatorio.** Sirve cualquier Python 3.10+ con `pycreate2` instalado. Alternativa con
> `venv` (sin conda): `python -m venv .venv`, activarlo (`.venv\Scripts\activate` en Windows) y
> `pip install -r requirements.txt`. El resto de esta guía (parche, puerto serie, problemas) es igual.

## 1. Crear el entorno (primera vez)

Desde la carpeta del proyecto:

```bat
conda env create -f environment.yml
conda activate create2
```

Si prefieres hacerlo a mano:

```bat
conda create -n create2 python=3.10
conda activate create2
pip install pycreate2==0.8.0
```

## 2. Parche de `get_sensors()` (solo una vez por entorno)

La versión de `pycreate2` instalada trae un `get_sensors()` con la indentación rota y no sabe
descartar los mensajes de texto que el robot envía al reiniciarse. El script
[`primeros_scripts/arreglar_get_sensors.py`](../primeros_scripts/arreglar_get_sensors.py) lo reescribe:

```bat
conda activate create2
python primeros_scripts\arreglar_get_sensors.py
```

Localiza `pycreate2` en el entorno activo, sustituye el método y comprueba que el archivo compila.
Hay que repetirlo si reinstalas o actualizas `pycreate2`.

## 3. Usar el entorno cada día

```bat
conda activate create2
cd ruta\al\proyecto
python teleoperacion\main.py
```

Para salir del entorno: `conda deactivate`.

## 4. Encontrar el puerto serie del robot

1. Enchufa el cable USB del Create 2 y enciende el robot.
2. Mira **Administrador de dispositivos → Puertos (COM y LPT)** o ejecuta:

   ```bat
   python -m serial.tools.list_ports -v
   ```

   Si sale `no ports found`, el robot no está conectado o falta el driver del adaptador.
3. Escribe el puerto en [`config.env`](../config.env) (`PUERTO=COM5`). No hay que tocar código.

## 5. Comandos útiles de conda

| Qué | Comando |
|---|---|
| Ver entornos | `conda env list` |
| Ver paquetes del entorno activo | `conda list` / `pip list` |
| Exportar el entorno | `conda env export --from-history > environment_minimo.yml` |
| Actualizar el entorno desde el `.yml` | `conda env update -f environment.yml --prune` |
| Borrar el entorno | `conda env remove -n create2` |

`environment_completo.yml` y `environment_minimo.yml` están en `.gitignore`: incluyen la ruta de tu
usuario (`prefix:`). El que se sube a GitHub es el `environment.yml` escrito a mano.

## 6. Problemas habituales

| Síntoma | Causa probable |
|---|---|
| `ModuleNotFoundError: pycreate2` | Entorno sin activar (`conda activate create2`). |
| `SerialException: could not open port 'COM5'` | Puerto equivocado en `config.env`, robot apagado u otro programa usando el puerto. |
| `RuntimeError: El robot no responde` | Robot dormido o batería baja: pulsa el botón Clean para despertarlo y reinicia el script. |
| El robot no obedece y la web muestra "Modo Passive" | Lo levantaron del suelo o detectó un desnivel. Ponlo en el suelo y usa **Reiniciar origen y control** (solo en `circuito`). |
| `OSError: [WinError 10048]` al arrancar | Ya hay otro script con la web abierta en el puerto 8000. Ciérralo o cambia `HTTP_PORT` en `config.env`. |
