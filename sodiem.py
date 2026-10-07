from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    request,
    url_for,
)
from markupsafe import escape
app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0},
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {},
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
}

def average(scores):
    """Tính trung bình cộng, làm tròn 2 chữ số; dict rỗng -> None."""
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    """Xếp loại điểm."""
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"


def student_summary(mssv):
    """Trả về dict tóm tắt thông tin sinh viên."""
    s = STUDENTS[mssv]
    avg = average(s["scores"])
    return {
        "mssv": mssv,
        "name": s["name"],
        "lop": s["lop"],
        "scores": s["scores"],
        "average": avg,
        "rank": rank(avg),
    }


def layout(title, body):
    """Khung trang HTML hoàn chỉnh, escape title, menu sinh bằng url_for."""
    home_url = url_for("home")
    students_url = url_for("student_list")
    search_url = url_for("search")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escape(title)} - Sổ điểm</title>
    <style>
        body {{ font-family: sans-serif; margin: 24px; line-height: 1.5; }}
        nav {{ margin-bottom: 20px; }}
        nav a {{ margin-right: 12px; text-decoration: none; color: #0366d6; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .filter-bar {{ margin-bottom: 15px; }}
        .filter-bar a {{ margin-right: 8px; }}
    </style>
</head>
<body>
    <nav>
        <a href="{home_url}">Trang chủ</a> ·
        <a href="{students_url}">Sinh viên</a> ·
        <a href="{search_url}">Tìm kiếm</a>
    </nav>
    <main>
        {body}
    </main>
</body>
</html>"""



@app.route("/")
def home():
    """Câu 1: Trang chủ."""
    total_students = len(STUDENTS)
    classes = {s["lop"] for s in STUDENTS.values()}
    total_classes = len(classes)

    students_link = url_for("student_list")
    api_students_link = url_for("api_student_list")

    body = f"""
    <h1>Tổng quan</h1>
    <p>Tổng số sinh viên: <strong>{escape(str(total_students))}</strong></p>
    <p>Số lớp: <strong>{escape(str(total_classes))}</strong></p>
    <ul>
        <li><a href="{students_link}">Xem danh sách sinh viên</a></li>
        <li><a href="{api_students_link}">API danh sách sinh viên</a></li>
    </ul>
    """
    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    """Câu 2: Danh sách sinh viên và bộ lọc theo lớp."""
    lop_filter = request.args.get("lop", "").strip()

    unique_classes = sorted({s["lop"] for s in STUDENTS.values()})

    filter_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for c in unique_classes:
        filter_links.append(
            f'<a href="{url_for("student_list", lop=c)}">{escape(c)}</a>'
        )
    filter_bar = ' | '.join(filter_links)

    # Lọc danh sách sinh viên
    matched = []
    for mssv in STUDENTS:
        summary = student_summary(mssv)
        if lop_filter:
            if summary["lop"].lower() == lop_filter.lower():
                matched.append(summary)
        else:
            matched.append(summary)

    if not matched:
        content = "<p>Không có sinh viên phù hợp.</p>"
    else:
        rows = []
        for s in matched:
            detail_link = url_for("student_detail", mssv=s["mssv"])
            avg_display = (
                "—" if s["average"] is None else f"{s['average']:.2f}"
            )
            rows.append(
                f"""<tr>
                <td><a href="{detail_link}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{escape(avg_display)}</td>
                <td>{escape(s['rank'])}</td>
            </tr>"""
            )
        content = f"""
        <table>
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    body = f"""
    <h1>Danh sách sinh viên</h1>
    <div class="filter-bar">{filter_bar}</div>
    {content}
    """
    return layout("Danh sách sinh viên", body)


@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    summary = student_summary(mssv)
    class_link = url_for("student_list", lop=summary["lop"])
    export_link = url_for("export_csv", mssv=mssv)
    short_link_url = url_for("short_link", mssv=mssv)

    avg_display = (
        "—" if summary["average"] is None else f"{summary['average']:.2f}"
    )

    rows = []
    for course, score in summary["scores"].items():
        rows.append(
            f"<tr><td>{escape(course)}</td><td>{escape(str(score))}</td></tr>"
        )

    score_table = (
        f"""<table>
        <thead><tr><th>Học phần</th><th>Điểm</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
    </table>"""
        if rows
        else "<p>Chưa có điểm môn nào.</p>"
    )

    body = f"""
    <h1>Thông tin sinh viên: {escape(summary['name'])}</h1>
    <p>MSSV: <strong>{escape(summary['mssv'])}</strong></p>
    <p>Lớp: <a href="{class_link}">{escape(summary['lop'])}</a></p>
    <p>Điểm TB: <strong>{escape(avg_display)}</strong></p>
    <p>Xếp loại: <strong>{escape(summary['rank'])}</strong></p>
    <p>Link rút gọn: <a href="{short_link_url}">{escape(short_link_url)}</a></p>
    <p><a href="{export_link}">Tải bảng điểm (CSV)</a></p>
    <h3>Bảng điểm</h3>
    {score_table}
    """
    return layout(summary["name"], body)

@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    csv_lines = ["hoc_phan,diem"]
    for course, sc in student["scores"].items():
        csv_lines.append(f"{course},{sc}")

    csv_body = "\n".join(csv_lines)
    response = make_response(csv_body)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )
    return response

@app.route("/sv/<mssv>")
def short_link(mssv):
    """Câu 4: Link rút gọn chuyển hướng 301."""
    return redirect(url_for("student_detail", mssv=mssv), code=301)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    q_clean = query.strip()
    search_url = url_for("search")
    results_html = ""

    if "q" in request.args:
        matched = []
        if q_clean:
            for mssv, data in STUDENTS.items():
                if (
                    q_clean.lower() in data["name"].lower()
                    or q_clean.lower() in mssv.lower()
                ):
                    matched.append((mssv, data["name"]))

        items = []
        for mssv, name in matched:
            detail_url = url_for("student_detail", mssv=mssv)
            items.append(
                f'<li><a href="{detail_url}">{escape(name)} ({escape(mssv)})</a></li>'
            )

        results_html = f"""
        <p>Tìm thấy {len(matched)} kết quả cho “{escape(query)}”</p>
        <ul>{''.join(items)}</ul>
        """

    body = f"""
    <h1>Tìm kiếm sinh viên</h1>
    <form method="GET" action="{search_url}">
        <input type="text" name="q" value="{escape(query)}" placeholder="Nhập tên hoặc MSSV...">
        <button type="submit">Tìm</button>
    </form>
    {results_html}
    """
    return layout("Tìm kiếm", body)


@app.route("/api/students")
def api_student_list():
    return "[]"
if __name__ == "__main__":
    app.run(debug=True, port=8000)