"""Command line interface for the attendance tracking app."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from .models import AttendanceRecord, Session
from .storage import JsonStorage

DEFAULT_DB_PATH = Path("data/attendance.json")
STATUS_LABELS = {"present": "presente", "absent": "ausente"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Registrar asistencia y tardanzas de estudiantes en clases",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Ruta al archivo JSON donde se guardan los datos (por defecto: data/attendance.json).",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Students -----------------------------------------------------------
    students = subparsers.add_parser("students", help="Operaciones relacionadas con estudiantes")
    student_sub = students.add_subparsers(dest="action", required=True)

    student_add = student_sub.add_parser("add", help="Registrar un nuevo estudiante")
    student_add.add_argument("name", help="Nombre completo del estudiante")

    student_sub.add_parser("list", help="Listar los estudiantes registrados")

    # Sessions -----------------------------------------------------------
    sessions = subparsers.add_parser("sessions", help="Operaciones relacionadas con clases")
    session_sub = sessions.add_subparsers(dest="action", required=True)

    session_add = session_sub.add_parser("add", help="Crear una nueva sesión de clase")
    session_add.add_argument("course", help="Nombre o descripción de la clase")
    session_add.add_argument(
        "date",
        help="Fecha programada (formato ISO: YYYY-MM-DD o YYYY-MM-DDTHH:MM)",
    )

    session_sub.add_parser("list", help="Listar sesiones disponibles")

    # Attendance ---------------------------------------------------------
    attendance = subparsers.add_parser(
        "attendance", help="Registrar y revisar la asistencia de los alumnos"
    )
    attendance_sub = attendance.add_subparsers(dest="action", required=True)

    mark = attendance_sub.add_parser(
        "mark", help="Registrar la asistencia de un estudiante en una sesión"
    )
    mark.add_argument("session_id", help="Identificador de la sesión")
    mark.add_argument("student_id", help="Identificador del estudiante")
    mark.add_argument(
        "--status",
        choices=["present", "absent"],
        default="present",
        help="Estado de asistencia (present o absent)",
    )
    mark.add_argument(
        "--late",
        action="store_true",
        help="Indica si el estudiante llegó tarde (solo válido con status=present)",
    )
    mark.add_argument("--notes", help="Notas adicionales", default=None)

    attendance_list = attendance_sub.add_parser(
        "list", help="Listar asistencia filtrada por sesión o estudiante"
    )
    attendance_list.add_argument("--session", dest="session_id", help="ID de sesión")
    attendance_list.add_argument("--student", dest="student_id", help="ID de estudiante")

    report = attendance_sub.add_parser(
        "report", help="Mostrar resumen de asistencia por sesión"
    )
    report.add_argument("session_id", help="Identificador de la sesión a reportar")

    return parser


def ensure_storage(path: Path) -> JsonStorage:
    return JsonStorage(path)


def cmd_students(storage: JsonStorage, action: str, args: argparse.Namespace) -> None:
    if action == "add":
        student = storage.add_student(args.name)
        print(f"✅ Estudiante agregado: {student.name} (id={student.id})")
    elif action == "list":
        students = storage.list_students()
        if not students:
            print("No hay estudiantes registrados todavía.")
            return
        print(format_table([("ID", "Nombre")], [(s.id, s.name) for s in students]))


def cmd_sessions(storage: JsonStorage, action: str, args: argparse.Namespace) -> None:
    if action == "add":
        session = storage.add_session(args.course, args.date)
        print(
            "✅ Sesión creada: {course} el {date} (id={id})".format(
                course=session.course,
                date=session.scheduled_at.strftime("%Y-%m-%d %H:%M"),
                id=session.id,
            )
        )
    elif action == "list":
        sessions = storage.list_sessions()
        if not sessions:
            print("No hay sesiones registradas todavía.")
            return
        headers = ("ID", "Curso", "Fecha programada")
        rows = [
            (
                session.id,
                session.course,
                session.scheduled_at.strftime("%Y-%m-%d %H:%M"),
            )
            for session in sessions
        ]
        print(format_table([headers], rows))


def cmd_attendance(storage: JsonStorage, action: str, args: argparse.Namespace) -> None:
    if action == "mark":
        record = storage.mark_attendance(
            args.session_id,
            args.student_id,
            args.status,
            late=args.late,
            notes=args.notes,
        )
        status_label = 'tarde' if record.late else STATUS_LABELS.get(record.status, record.status)
        print(
            "✅ Asistencia registrada: estudiante={student} sesión={session} estado={status}".format(
                student=record.student_id,
                session=record.session_id,
                status=status_label,
            )
        )
    elif action == "list":
        session_id = args.session_id
        student_id = args.student_id
        records = storage.list_attendance()
        if session_id:
            records = [r for r in records if r.session_id == session_id]
        if student_id:
            records = [r for r in records if r.student_id == student_id]
        if not records:
            print("No hay registros que coincidan con el filtro indicado.")
            return
        headers = ("ID", "Sesión", "Estudiante", "Estado", "Tarde", "Notas")
        rows = [
            (
                record.id,
                record.session_id,
                record.student_id,
                STATUS_LABELS.get(record.status, record.status),
                "sí" if record.late else "no",
                record.notes or "-",
            )
            for record in records
        ]
        print(format_table([headers], rows))
    elif action == "report":
        session_id = args.session_id
        session = next((s for s in storage.list_sessions() if s.id == session_id), None)
        if not session:
            print("La sesión indicada no existe.")
            return
        records = storage.attendance_for_session(session_id)
        if not records:
            print("Todavía no hay asistencias cargadas para esta sesión.")
            return
        print(
            f"Resumen de asistencia para {session.course} el {session.scheduled_at.strftime('%Y-%m-%d %H:%M')}"
        )
        totals = summarize_attendance(records)
        for status, total in totals:
            print(f"- {status}: {total}")


def summarize_attendance(records: Iterable[AttendanceRecord]) -> List[Tuple[str, int]]:
    present = sum(1 for record in records if record.status == "present" and not record.late)
    late = sum(1 for record in records if record.status == "present" and record.late)
    absent = sum(1 for record in records if record.status == "absent")
    return [
        ("Presentes", present),
        ("Presentes (tarde)", late),
        ("Ausentes", absent),
    ]


def format_table(headers: List[Tuple[str, ...]], rows: List[Tuple[str, ...]]) -> str:
    """Simple helper to create aligned text tables."""

    columns = len(headers[0])
    widths = [0] * columns
    for row in [headers[0], *rows]:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))
    lines = []
    header_line = " | ".join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(headers[0]))
    separator = "-+-".join("-" * widths[idx] for idx in range(columns))
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        lines.append(" | ".join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(row)))
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = ensure_storage(args.db)

    if args.command == "students":
        cmd_students(storage, args.action, args)
    elif args.command == "sessions":
        cmd_sessions(storage, args.action, args)
    elif args.command == "attendance":
        cmd_attendance(storage, args.action, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
