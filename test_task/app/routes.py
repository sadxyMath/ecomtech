from fastapi import APIRouter, UploadFile, File
import csv
import io
from datetime import datetime
from app.database import get_connection
from typing import List
from app.schemas import UploadResponse, StudentTwos

router = APIRouter()

@router.post("/upload-grades", response_model=UploadResponse)
async def upload_grades(file: UploadFile = File(...)):

    content = await file.read()
    reader = csv.DictReader(
        io.StringIO(content.decode("utf-8-sig")),
        delimiter=";"
    )

    conn = get_connection()
    cur = conn.cursor()

    records = 0
    students = set()

    for row in reader:
        try:
            exam_date = datetime.strptime(row["Дата"].strip(), "%d.%m.%Y").date()
            group = row["Номер группы"].strip()
            full_name = row["ФИО"].strip()
            grade = int(row["Оценка"])

            if grade < 2 or grade > 5:
                continue

            cur.execute(
                """
                INSERT INTO grades (exam_date, group_name, full_name, grade)
                VALUES (%s,%s,%s,%s)
                """,
                (exam_date, group, full_name, grade)
            )

            records += 1
            students.add(full_name)

        except Exception as e:
            print("Ошибка в строке:", row, ">", e)
            continue

    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "ok",
        "records_loaded": records,
        "students": len(students)
    }


@router.get("/students/more-than-3-twos", response_model=List[StudentTwos])
def more_than_3_twos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT full_name, COUNT(*) as count_twos
        FROM grades
        WHERE grade = 2
        GROUP BY full_name
        HAVING COUNT(*) > 3
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"full_name": r[0], "count_twos": r[1]}
        for r in rows
    ]

@router.get("/students/less-than-5-twos", response_model=List[StudentTwos])
def less_than_5_twos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT full_name, COUNT(*) as count_twos
        FROM grades
        WHERE grade = 2
        GROUP BY full_name
        HAVING COUNT(*) < 5
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"full_name": r[0], "count_twos": r[1]}
        for r in rows
    ]