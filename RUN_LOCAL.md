# RUN_LOCAL.md – Hướng dẫn chạy Lab 04

Tài liệu này giúp người khác clone repo sạch và chạy lại service **Access Gate** trong Docker.

---

## 1. Clone repo

```bash
git clone <repo-url>
cd lab04-phamtuananh05
```

Nếu tên thư mục repo khác, chuyển vào đúng thư mục chứa `Dockerfile`, `package.json`, `src/`, `contracts/`, `postman/`.

---

## 2. Cài dependencies cho Newman/Prism/Spectral

```bash
npm install
```

Kiểm tra Newman:

```bash
npx newman --version
```

---

## 3. Build Docker image

```bash
docker build -t fit4110/access-gate:lab04 .
```

Gắn thêm tag theo quy ước Lab 04:

```bash
docker tag fit4110/access-gate:lab04 fit4110/access-gate:v0.1.0-team-gate
```

Kiểm tra image:

```bash
docker images
```

---

## 4. Run Access Gate container

```bash
docker run --rm \
  --name fit4110-access-gate-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/access-gate:lab04
```

Trên Windows PowerShell, có thể dùng một dòng:

```powershell
docker run --rm --name fit4110-access-gate-lab04 -p 8000:8000 --env-file .env.example fit4110/access-gate:lab04
```

Mở terminal khác, kiểm tra:

```bash
curl -i http://localhost:8000/health
```

Kết quả mong đợi:

```json
{
  "status": "ok",
  "service": "access-gate"
}
```

---

## 5. Chạy Core Business mock cho consumer-side smoke test

Postman Collection có một request consumer-side smoke gọi Core Business mock tại port `4011`, vì vậy cần mở thêm một terminal khác và chạy:

```bash
npx prism mock contracts/core-business.openapi.yaml -p 4011 --host 0.0.0.0
```

Kiểm tra mock:

```bash
curl -i http://localhost:4011/health
```

---

## 6. Chạy Newman test trên container

Khi Access Gate container đang chạy ở `http://localhost:8000` và Core Business mock đang chạy ở `http://localhost:4011`, chạy:

```bash
npm run test:local
```

Report sinh tại:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
```

---

## 7. Dừng container

Nếu container đang chạy ở terminal hiện tại, bấm:

```text
Ctrl + C
```

Nếu container chạy nền hoặc vẫn còn tồn tại:

```bash
docker stop fit4110-access-gate-lab04
```

---

## 8. Lệnh kiểm tra nhanh

```bash
docker build -t fit4110/access-gate:lab04 .
docker tag fit4110/access-gate:lab04 fit4110/access-gate:v0.1.0-team-gate
docker run --rm --name fit4110-access-gate-lab04 -p 8000:8000 --env-file .env.example fit4110/access-gate:lab04
curl -i http://localhost:8000/health
npm run test:local
```

---

## 9. Ghi chú

* Lab 04 dùng dữ liệu in-memory cho Access Gate, chưa kết nối database thật.
* Các biến môi trường mẫu được khai báo trong `.env.example`.
* Không commit secret thật vào repo.
