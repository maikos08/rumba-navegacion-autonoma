"""
Reescribe get_sensors() en create2api.py con la indentación correcta.
Uso (con el entorno create2 activado):
    python arreglar_get_sensors.py
"""
import importlib.util
import re
from pathlib import Path

# Localiza pycreate2 en el entorno activo sin importarlo (el archivo roto no compilaría)
_spec = importlib.util.find_spec("pycreate2")
if _spec is None or not _spec.submodule_search_locations:
    raise SystemExit("pycreate2 no está instalado en este entorno. Activa el entorno 'create2'.")
RUTA = Path(list(_spec.submodule_search_locations)[0]) / "create2api.py"

NUEVA = '''    def get_sensors(self):
        opcode = OPCODES.SENSORS
        cmd = (100,)
        sensor_pkt_len = 80

        self.SCI.write(opcode, cmd)
        time.sleep(0.015)  # wait 15 msec

        packet_byte_data = self.SCI.read(sensor_pkt_len)

        flash_msg = packet_byte_data.find(b'(0x0)\\n\\r')
        wakeup_msg = packet_byte_data.find(b'conds\\r\\n')
        msg = max(flash_msg, wakeup_msg)

        if not msg == -1:
            print(packet_byte_data)
            packet_byte_data_continue = self.SCI.read(msg + 7)
            packet_byte_data = packet_byte_data[msg + 7:] + packet_byte_data_continue

        sensors = SensorPacketDecoder(packet_byte_data)

        return sensors

'''

with open(RUTA, encoding="utf-8") as f:
    texto = f.read().expandtabs(4)

# Desde "def get_sensors" hasta el siguiente método de la clase (o fin de archivo)
patron = re.compile(r"^[ ]*def get_sensors\(self\):.*?(?=^    def |^    @|^class |\Z)",
                    re.DOTALL | re.MULTILINE)

if not patron.search(texto):
    raise SystemExit("No se encontró 'def get_sensors(self):' en el archivo.")

texto = patron.sub(lambda m: NUEVA, texto, count=1)

with open(RUTA, "w", encoding="utf-8") as f:
    f.write(texto)

# Comprobación de sintaxis
compile(texto, RUTA, "exec")
print("get_sensors() reescrita y el archivo compila correctamente.")
