# BÀI TẬP TỔNG HỢP CHƯƠNG 3 - QUẢN LÝ SỔ ĐIỂM FLASK

## 1. Kết quả `flask --app sodiem routes`

```text
Endpoint            Methods           Rule
------------------  ----------------  --------------------------------------------------
api_score_course    DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
api_student_detail  GET               /api/students/<mssv>
api_student_list    GET               /api/students
export_csv          GET               /students/<mssv>/export
home                GET               /
search              GET               /search
short_link          GET               /sv/<mssv>
static              GET               /static/<path:filename>
student_detail      GET               /students/<mssv>
student_list        GET               /students
```

---

## 2. Dòng trạng thái và body của từng lệnh `curl`

### Lệnh 1: `curl -i $B/sv/23T1020001`
- **Dòng trạng thái:** `HTTP/1.1 301 MOVED PERMANENTLY`
- **Header quan trọng:** `Location: /students/23T1020001`

### Lệnh 2: `curl -i $B/students/23T1020001/export`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Header quan trọng:**
  - `Content-Type: text/csv; charset=utf-8`
  - `Content-Disposition: attachment; filename=diem_23T1020001.csv`
- **Body:**
  ```csv
  hoc_phan,diem
  PMMNM,8.5
  CSDL,7.0
  MMT,9.0
  ```

### Lệnh 3: `curl "$B/api/students?lop=k47a&min_avg=7"`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Body:**
  ```json
  [
    {
      "average": 8.17,
      "lop": "K47A",
      "mssv": "23T1020001",
      "name": "Nguyễn Văn An",
      "rank": "Khá",
      "scores": {
        "CSDL": 7.0,
        "MMT": 9.0,
        "PMMNM": 8.5
      }
    }
  ]
  ```

### Lệnh 4: `curl -i "$B/api/students?min_avg=abc"`
- **Dòng trạng thái:** `HTTP/1.1 400 BAD REQUEST`
- **Body:**
  ```json
  {
    "detail": "Tham số min_avg phải là số thực.",
    "error": "Dữ liệu không hợp lệ"
  }
  ```

### Lệnh 5: `curl -i $B/api/students/999`
- **Dòng trạng thái:** `HTTP/1.1 404 NOT FOUND`
- **Body:**
  ```json
  {
    "detail": "Không có sinh viên với MSSV = 999.",
    "error": "Không tìm thấy"
  }
  ```

### Lệnh 6: `curl -i -X PUT "$S/web?score=9"`
- **Dòng trạng thái:** `HTTP/1.1 201 CREATED`
- **Header quan trọng:** `Location: /api/students/23T1020005/scores/WEB`
- **Body:**
  ```json
  {
    "average": 9.0,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 9.0
  }
  ```

### Lệnh 7: `curl -X PUT "$S/WEB?score=7.5"`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Body:**
  ```json
  {
    "average": 7.5,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 7.5
  }
  ```

### Lệnh 8: `curl -i -X PUT "$S/WEB?score=11"`
- **Dòng trạng thái:** `HTTP/1.1 400 BAD REQUEST`
- **Body:**
  ```json
  {
    "detail": "Điểm phải nằm trong đoạn [0, 10].",
    "error": "Dữ liệu không hợp lệ"
  }
  ```

### Lệnh 9: `curl -i -X DELETE $S/WEB`
- **Dòng trạng thái:** `HTTP/1.1 204 NO CONTENT`
- **Body:** *(Rỗng)*

### Lệnh 10: `curl -i -X POST $S/WEB`
- **Dòng trạng thái:** `HTTP/1.1 405 METHOD NOT ALLOWED`
- **Body:**
  ```json
  {
    "detail": "The method is not allowed for the requested URL.",
    "error": "Phương thức không được hỗ trợ"
  }
  ```

### Lệnh 11: `curl -i -X POST $B/students`
- **Dòng trạng thái:** `HTTP/1.1 405 METHOD NOT ALLOWED`
- **Content-Type:** `text/html; charset=utf-8`
- **Body:** Trang HTML thông báo lỗi 405 hiển thị qua khung `layout()`.

---

## 3. Trả lời câu hỏi lý thuyết

### 3.1. Vì sao dùng được `request` trong hàm `handle_error` dù nó không phải view function?
Trong kiến trúc của Flask, `request` là một *context-local proxy*. Khi một client gửi HTTP request đến server, Flask khởi tạo một **Request Context** bao trùm toàn bộ chu trình xử lý request đó. Khi xảy ra lỗi hoặc ngoại lệ, hàm `@app.errorhandler` được kích hoạt và chạy bên trong Request Context này. Do đó biến toàn cục cục bộ `request` vẫn hợp lệ và trỏ đúng vào request đang được xử lý.

### 3.2. Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?
- **Mã 301 (Moved Permanently):** Dùng để chuyển hướng URL cố định từ liên kết rút gọn (`/sv/<mssv>`) sang URL chính thức (`/students/<mssv>`). Trình duyệt có thể lưu bộ nhớ đệm (cache) để các lần sau truy cập thẳng đến URL đích.
- **Mã 201 (Created) kèm `Location`:** Tuân thủ chuẩn RESTful API. Khi thao tác `PUT` tạo mới thành công một tài nguyên chưa từng tồn tại trên server, status 201 xác nhận tài nguyên đã được tạo, và header `Location` cung cấp URL trực tiếp để truy cập đến tài nguyên đó.

### 3.3. Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm đó còn không? Vì sao?
- **Kết quả:** Điểm đó **không còn**.
- **Giải thích:** Dữ liệu `STUDENTS` hiện được lưu trong biến kiểu `dict` trên bộ nhớ RAM của tiến trình Python (*in-memory*). Khi server khởi động lại, tiến trình bị giải phóng và dữ liệu trong RAM mất đi. Ứng dụng sẽ nạp lại dữ liệu khởi tạo ban đầu được định nghĩa cứng trong file `sodiem.py`.