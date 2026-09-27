# Yerqz Pinger

Pinger con interfaz gráfica hecho en Python. Metes una IP o dominio, le das a PING y ves los resultados en tiempo real.

## Qué tiene

- Interfaz en Tkinter con tema rojo/negro
- Título ASCII con degradado rojo generado con PIL
- GIF animado de fondo
- Log con etiquetas de color: verde para `CONNECTED`, rojo para `DOWNED`
- Estadísticas en vivo: enviados, online, Offline, pérdida, mín/máx/promedio
- Exportación a CSV
- Funciona en Windows

## Instalación

Necesitas Python 3.8 o superior y Pillow.

```
pip install pillow
```
Coloca tu GIF en la misma carpeta que el script y llámalo `fondo.gif`.

Hay dos formas de ejecutarlo:

**Opción 1: Con Python directamente**`

```
python yerqzpinger.py
```

**Opción 2: Con el archivo .bat (mejor y mas rapido)**`

Haz doble clic en `start.bat`.