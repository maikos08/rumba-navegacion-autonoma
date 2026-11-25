"""
ÚNICO servidor HTTP del proyecto. Sirve la página de cualquier tarea:

  GET  /            -> el ui.html de la tarea
  GET  /static/<f>  -> archivos comunes (mapa.js, base.css)
  GET  /estado?...  -> tarea.estado_web(args) como JSON
  POST /<ruta>?...  -> tarea.acciones_web()[ruta](args)   (204 ok, 400 args inválidos, 404 no existe)

Solo habla con el objeto `tarea` (ver rumba/ejecutar.py), no sabe nada de robots.
"""
import json
import mimetypes
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ESTATICOS = Path(__file__).resolve().parent / "static"


class ServidorWeb:
    def __init__(self, tarea, host, puerto):
        self.tarea = tarea
        self.url = f"http://{host}:{puerto}"
        self.httpd = ThreadingHTTPServer((host, puerto), self._crear_handler())

    def iniciar(self, abrir_navegador=True):
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        if abrir_navegador:
            webbrowser.open(self.url)

    def detener(self):
        self.httpd.shutdown()

    def _crear_handler(self):
        tarea = self.tarea

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass  # no llenar la consola con cada petición

            def enviar(self, codigo, cuerpo=b"", tipo="text/plain"):
                self.send_response(codigo)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(cuerpo)))
                self.end_headers()
                self.wfile.write(cuerpo)

            def do_GET(self):
                url = urlparse(self.path)
                args = {k: v[0] for k, v in parse_qs(url.query).items()}
                if url.path == "/":
                    self.enviar(200, Path(tarea.pagina).read_bytes(), "text/html; charset=utf-8")
                elif url.path == "/estado":
                    try:
                        with tarea.lock:
                            datos = tarea.estado_web(args)
                    except (ValueError, KeyError):
                        self.enviar(400)
                        return
                    self.enviar(200, json.dumps(datos).encode(), "application/json")
                elif url.path.startswith("/static/"):
                    archivo = (ESTATICOS / url.path[len("/static/"):]).resolve()
                    if archivo.parent != ESTATICOS or not archivo.is_file():
                        self.enviar(404)
                        return
                    tipo = mimetypes.guess_type(archivo.name)[0] or "application/octet-stream"
                    self.enviar(200, archivo.read_bytes(), tipo + "; charset=utf-8")
                else:
                    self.enviar(404)

            def do_POST(self):
                url = urlparse(self.path)
                args = {k: v[0] for k, v in parse_qs(url.query).items()}
                accion = tarea.acciones_web().get(url.path)
                if accion is None:
                    self.enviar(404)
                    return
                try:
                    with tarea.lock:
                        accion(args)
                except (ValueError, KeyError):
                    self.enviar(400)
                    return
                self.enviar(204)

        return Handler
