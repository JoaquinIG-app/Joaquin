# Registro de asistencia

Aplicación de línea de comandos para registrar la asistencia de tus alumnos a clase, incluyendo si llegaron tarde.

## Requisitos

- Python 3.9 o superior (incluido en la mayoría de los entornos modernos)

## Instalación

Clona el repositorio y, opcionalmente, crea un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

No hay dependencias externas, por lo que no es necesario instalar paquetes adicionales.

## Uso

Todos los datos se guardan en un archivo JSON ubicado en `data/attendance.json`. Puedes cambiar la ruta con el parámetro `--db` en cualquier comando.

Ejemplos de uso:

1. **Agregar un estudiante**

```bash
python attendance.py students add "Ana Pérez"
```

2. **Listar estudiantes**

```bash
python attendance.py students list
```

3. **Crear una sesión de clase**

```bash
python attendance.py sessions add "Matemáticas" 2024-03-18T08:00
```

4. **Listar sesiones**

```bash
python attendance.py sessions list
```

5. **Registrar asistencia**

```bash
python attendance.py attendance mark <SESSION_ID> <STUDENT_ID> --status present --late
```

- `--status` puede ser `present` o `absent`.
- `--late` indica que el alumno llegó tarde (solo válido cuando `--status present`).

6. **Ver registros de asistencia**

```bash
python attendance.py attendance list --session <SESSION_ID>
```

7. **Obtener un resumen por sesión**

```bash
python attendance.py attendance report <SESSION_ID>
```

## Notas

- Si vuelves a registrar la asistencia para la misma combinación de sesión y alumno, el registro anterior se reemplaza.
- El formato de fecha debe ser ISO (`YYYY-MM-DD` o `YYYY-MM-DDTHH:MM`).
