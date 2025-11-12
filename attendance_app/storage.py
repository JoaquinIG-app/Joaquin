"""Persistent storage utilities for the attendance app."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from .models import AttendanceRecord, Session, Student


class StorageError(RuntimeError):
    """Raised when there is a persistence related error."""


class JsonStorage:
    """Very small JSON-based persistence layer."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"students": [], "sessions": [], "attendance": []})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _read(self) -> Dict[str, List[Dict[str, object]]]:
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            raise StorageError("Los datos de asistencia están corruptos.") from exc

    def _write(self, data: Dict[str, List[Dict[str, object]]]) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Student management
    # ------------------------------------------------------------------
    def list_students(self) -> List[Student]:
        return [Student.from_dict(raw) for raw in self._read()["students"]]

    def add_student(self, name: str) -> Student:
        if not name.strip():
            raise ValueError("El nombre del estudiante no puede estar vacío.")
        data = self._read()
        students = data["students"]
        new_student = Student(id=str(uuid.uuid4()), name=name.strip())
        students.append(new_student.to_dict())
        data["students"] = students
        self._write(data)
        return new_student

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------
    def list_sessions(self) -> List[Session]:
        return [Session.from_dict(raw) for raw in self._read()["sessions"]]

    def add_session(self, course: str, scheduled_at: str) -> Session:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
        except ValueError as exc:
            raise ValueError(
                "Formato de fecha inválido. Usa YYYY-MM-DD o una fecha ISO válida."
            ) from exc
        data = self._read()
        session = Session(
            id=str(uuid.uuid4()),
            course=course.strip(),
            scheduled_at=scheduled_dt,
        )
        sessions = data["sessions"]
        sessions.append(session.to_dict())
        data["sessions"] = sessions
        self._write(data)
        return session

    # ------------------------------------------------------------------
    # Attendance management
    # ------------------------------------------------------------------
    def list_attendance(self) -> List[AttendanceRecord]:
        return [AttendanceRecord.from_dict(raw) for raw in self._read()["attendance"]]

    def mark_attendance(
        self,
        session_id: str,
        student_id: str,
        status: str,
        *,
        late: bool = False,
        notes: Optional[str] = None,
    ) -> AttendanceRecord:
        data = self._read()
        if session_id not in {session["id"] for session in data["sessions"]}:
            raise ValueError("La sesión indicada no existe.")
        if student_id not in {student["id"] for student in data["students"]}:
            raise ValueError("El estudiante indicado no existe.")

        record = AttendanceRecord(
            id=str(uuid.uuid4()),
            session_id=session_id,
            student_id=student_id,
            status=status,
            late=late,
            notes=notes,
        )
        attendance = data["attendance"]
        # Remove existing record for same student/session to keep last update.
        attendance = [
            raw
            for raw in attendance
            if not (raw["session_id"] == session_id and raw["student_id"] == student_id)
        ]
        attendance.append(record.to_dict())
        data["attendance"] = attendance
        self._write(data)
        return record

    def attendance_for_session(self, session_id: str) -> List[AttendanceRecord]:
        return [
            record
            for record in self.list_attendance()
            if record.session_id == session_id
        ]

    def attendance_for_student(self, student_id: str) -> List[AttendanceRecord]:
        return [
            record
            for record in self.list_attendance()
            if record.student_id == student_id
        ]
