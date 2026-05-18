COMMAND: /log-bug

Title: Khong tao duoc phieu nhap kho khi so luong = 0
Environment: STG 1.0.9 (2)
Platform: Web

Actual:
- Mo man hinh Tao phieu nhap
- Chon nha cung cap SUP001
- Nhap so luong = 0
- Bam Luu
- He thong khong bao loi, record van duoc tao

Expected:
- Validate va chan Luu khi so luong <= 0
- Hien thong bao loi ro rang tai field So luong

Additional info:
- Dev PIC: Phuong
- Sprint: 1-2026/4
- Tinh nang: Kho / Nhap kho
