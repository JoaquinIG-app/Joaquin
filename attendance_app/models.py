"""Domain models for the attendance tracking application."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Student:
    """Represents a student that can attend classes."""

    id: str
    name: str

    def to_dict(self) -> Dict[str, str]:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Student":
        return cls(id=data["id"], name=data["name"])


@dataclass
class Session:
    """Represents a class session."""

    id: str
    course: str
    scheduled_at: datetime

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "course": self.course,
            "scheduled_at": self.scheduled_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Session":
        return cls(
            id=data["id"],
            course=data["course"],
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]),
        )


@dataclass
class AttendanceRecord:
    """Stores the attendance status of a student in a session."""

    id: str
    session_id: str
    student_id: str
    status: str
    late: bool = False
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        allowed = {"present", "absent"}
        if self.status not in allowed:
            raise ValueError(
                f"Estado de asistencia inválido '{self.status}'. Opciones: {sorted(allowed)}"
            )
        if self.late and self.status != "present":
            raise ValueError("Solo se puede marcar 'late' si el estudiante está presente.")

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "student_id": self.student_id,
            "status": self.status,
            "late": self.late,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str]]) -> "AttendanceRecord":
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            student_id=data["student_id"],
            status=data["status"],
            late=bool(data.get("late", False)),
            notes=data.get("notes"),
        )


def group_attendance_by_student(records: List[AttendanceRecord]) -> Dict[str, List[AttendanceRecord]]:
    grouped: Dict[str, List[AttendanceRecord]] = {}
    for record in records:
        grouped.setdefault(record.student_id, []).append(record)
    return grouped


def group_attendance_by_session(records: List[AttendanceRecord]) -> Dict[str, List[AttendanceRecord]]:
    grouped: Dict[str, List[AttendanceRecord]] = {}
    for record in records:
        grouped.setdefault(record.session_id, []).append(record)
    return grouped
