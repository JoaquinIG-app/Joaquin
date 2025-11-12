from pathlib import Path

from attendance_app.storage import JsonStorage


def test_add_student_and_session(tmp_path: Path) -> None:
    storage = JsonStorage(tmp_path / "data.json")
    student = storage.add_student("Juan")
    session = storage.add_session("Historia", "2024-04-05T09:00")

    assert student.name == "Juan"
    assert session.course == "Historia"
    assert storage.list_students()[0].id == student.id
    assert storage.list_sessions()[0].id == session.id


def test_mark_attendance(tmp_path: Path) -> None:
    storage = JsonStorage(tmp_path / "data.json")
    student = storage.add_student("Lucía")
    session = storage.add_session("Geografía", "2024-04-06T10:00")

    record = storage.mark_attendance(session.id, student.id, "present", late=True)
    assert record.late is True
    assert storage.attendance_for_session(session.id)[0].late is True

    # Reemplaza el registro anterior
    storage.mark_attendance(session.id, student.id, "absent", late=False)
    records = storage.attendance_for_session(session.id)
    assert len(records) == 1
    assert records[0].status == "absent"
