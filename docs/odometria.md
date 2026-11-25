# Odometría del Create 2

La **odometría** estima la posición del robot (dead-reckoning) integrando el giro de sus ruedas.
Es la única localización que usa este proyecto: no hay mapa ni balizas, así que **el origen (0, 0, 0°)
es donde arranca el robot**, con x hacia delante e y hacia la izquierda.

Implementación: [`rumba/robot.py`](../rumba/robot.py) (la clase `Odometria`).
Teoría del curso: tema 3 (secciones *Sensores de odometría*, *Encoders* y *Errores de odometría*) y
tema 5.1 (*dead-reckoning* dentro de la capacidad de navegación). Esos apuntes no se incluyen en el repositorio.

## 1. De cuentas de encoder a milímetros

Cada rueda del Create 2 tiene un encoder incremental. El Open Interface devuelve un contador de
**16 bits sin signo** (`encoder_counts_left` / `encoder_counts_right`):

| Dato (spec Open Interface) | Valor | Clave en `config.env` |
|---|---|---|
| Diámetro de rueda | 72 mm | `DIAMETRO_RUEDA` |
| Cuentas por vuelta de rueda | 508,8 | `CUENTAS_POR_VUELTA` |
| Distancia entre ruedas | 235 mm | `B` |

```
mm_por_cuenta = π · 72 / 508,8 ≈ 0,4446 mm
```

El contador se desborda (65535 → 0), así que la diferencia entre dos lecturas se calcula en
aritmética modular (`Odometria._delta`):

```python
delta = (nuevo - anterior + 32768) % 65536 - 32768   # positivo = rueda avanzó
```

## 2. Modelo de tracción diferencial

Con `Δs_r` y `Δs_l` el camino recorrido por cada rueda en un paso (en mm):

```
Δs  = (Δs_r + Δs_l) / 2        avance del centro del robot
Δθ  = (Δs_r − Δs_l) / B        giro (rad, positivo = antihorario / izquierda)

x  ← x + Δs · cos(θ + Δθ)
y  ← y + Δs · sin(θ + Δθ)
θ  ← θ + Δθ
```

Es la expresión del tema 3 (`ΔS = (ΔS₁+ΔS₂)/2`, `Δθ = (ΔS₂−ΔS₁)/D`), con `D = B`.

Casos límite que conviene tener en la cabeza:

| Movimiento | `Δs_r` vs `Δs_l` | Resultado |
|---|---|---|
| Recto | iguales | `Δθ = 0`, solo cambia (x, y) |
| Giro sobre sí mismo | opuestos | `Δs = 0`, solo cambia θ |
| Arco | distintos, mismo signo | cambian las tres |

## 3. Ciclo de lectura

[`rumba/ejecutar.py`](../rumba/ejecutar.py) llama a `Odometria.actualizar()` cada `PERIODO` = 50 ms
(la especificación pide no pedir sensores más rápido que cada 15 ms):

1. Lee los encoders (`Robot.leer()`).
2. `ds, dtheta = odometria.actualizar(enc_l, enc_r)`.
3. Entrega pose, `ds` y `dtheta` a la tarea en el objeto `Marco`.

`ds` y `dtheta` se publican también porque algunas tareas los usan directamente: el circuito
descuenta `dtheta` para saber cuánto falta de un giro, y Bug2 suma `|ds|` para limitar el recorrido
siguiendo paredes.

## 4. Fuentes de error

Del tema 3, adaptado al Create 2:

| Tipo | Causa | Qué se nota |
|---|---|---|
| Sistemático | Diámetro de rueda real distinto de 72 mm, `B` mal medido, ruedas desiguales | El cuadrado de 1 m no cierra siempre igual: deriva constante |
| No sistemático | Deslizamiento (suelo resbaladizo, alfombra), objetos en el suelo, giros bruscos | Errores distintos en cada ejecución |
| De integración | Aproximar el arco por un tramo recto | Crece con pasos grandes o giros rápidos |

El error **se acumula**: la posición nunca se corrige con información externa. Para trayectos cortos
(1-3 m) es suficiente; para recorridos largos haría falta fusionar otro sensor (ver el tema 5,
localización).

### Calibración rápida

1. Con `teleoperacion`, avanza ~1 m midiendo con cinta y compara con la x que muestra la página.
   Si difiere un `k` %, ajusta `DIAMETRO_RUEDA` (o `CUENTAS_POR_VUELTA`) en `config.env`.
2. Gira sobre sí mismo una vuelta completa (la página debe marcar ±360°). Si no cierra, ajusta `B`.
3. Repite varias veces y usa la media: un solo intento mezcla error sistemático y no sistemático.

## 5. Mejoras posibles

* **Integración de punto medio**: usar `θ + Δθ/2` en lugar de `θ + Δθ` para `x` e `y`. Es el
  esquema habitual y reduce el error en arcos cerrados. No se ha cambiado para no alterar el
  comportamiento ya probado con el robot.
* **Script de calibración** que automatice los pasos anteriores y escriba el resultado en `config.env`.
* **Modelo de error** (covarianza) para saber cuánto fiarse de la pose, como en el tema 5.
