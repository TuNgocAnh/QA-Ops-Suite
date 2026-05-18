# Sitemap Rules

Rules về đọc, sử dụng, và tự động làm giàu sitemap.
**Đọc khi**: `/cook`, `/fix`, `/analyze`, `/plan-tc`

---

## 1. Khi nào đọc sitemap

- **LUÔN** đọc `.claude/sitemap.yaml` ở đầu mọi command (`/cook`, `/fix`, `/analyze`, `/plan-tc`)
- Nếu sitemap trống (chỉ có example/comment) => bỏ qua bước sử dụng, nhưng **vẫn enrich** sau khi xong
- `/ask` và `/est-sp`: đọc on-demand khi cần context về luồng hoặc impact

---

## 2. Sử dụng sitemap trong từng command

### 2.1 Sinh Precondition (`/cook`, `/fix`)
- Tra `pages[feature].nav_steps` + parent chain => sinh precondition đầy đủ
- Nếu `auth_required: true` => thêm "Đã đăng nhập với role [roles]"
- Nếu có `flows` liên quan => reference flow thay vì viết lại steps
- **Ví dụ**: Feature `invoice_create` có `nav_steps: "Sidebar > Hóa đơn > Danh sách > Nhấn 'Tạo mới'"` và `auth_required: true`, `roles: ["admin", "accountant"]`
  => Precondition: "Đã đăng nhập với tài khoản admin/accountant, truy cập Sidebar > Hóa đơn > Danh sách > Nhấn nút 'Tạo mới'"

### 2.2 Đánh giá Impact (`/cook`, `/fix`)
- Đọc `features[feature].impacts` => danh sách feature bị ảnh hưởng
- **`/cook`**: Thêm ít nhất 1 TC per impact để verify cross-feature (section riêng "Cross-Feature Impact")
- **`/fix`**: Khi fix bug => tra impact map => xác định regression scope => sinh regression TC cho các feature bị ảnh hưởng
- Impact types:
  - `data_change`: Dữ liệu thay đổi ở feature khác
  - `navigation`: Luồng điều hướng bị ảnh hưởng
  - `permission`: Quyền truy cập thay đổi
  - `notification`: Thông báo/email bị ảnh hưởng

### 2.3 Kiểm tra Dependencies (`/cook`)
- Đọc `features[feature].depends_on` => đảm bảo precondition đủ
- Sinh edge case TC cho trường hợp dependency không thỏa mãn
- **Ví dụ**: `invoice_create` depends_on `supplier_list` => TC: "Tạo hóa đơn khi chưa có NCC nào trong hệ thống"

### 2.4 Reuse Shared Flows (`/cook`, `/fix`)
- Tra `flows` => nếu feature nằm trong `used_by` => reuse flow steps
- Tránh viết lặp cùng 1 luồng thao tác ở nhiều TC

### 2.5 Phân tích (`/analyze`)
- Dùng sitemap để so sánh scope hiện tại vs scope mới từ requirement
- Phát hiện feature mới chưa có trong sitemap
- Phát hiện thay đổi luồng (nav_steps khác so với requirement mới)

### 2.6 Lập kế hoạch (`/plan-tc`)
- Dùng impact map để đánh giá scope regression khi plan
- Dùng dependencies để xác định thứ tự ưu tiên test
- Thêm section "Impact Analysis" trong plan nếu feature có impacts

---

## 3. Auto-Enrich Rules (MANDATORY)

### 3.1 Khi nào enrich
- **SAU** mỗi `/cook`: cập nhật `tc_history` (last_cook, tc_count, sheets_url)
- **SAU** mỗi `/fix`: cập nhật `known_bugs`, thêm impact mới nếu phát hiện
- **SAU** mỗi `/analyze`: thêm pages/features/flows mới từ requirement
- **SAU** mỗi `/plan-tc`: thêm features mới vào registry nếu chưa có
- Enrich xong => cập nhật `last_updated`

### 3.2 Nguyên tắc enrich
- **CHỈ THÊM hoặc CẬP NHẬT**, không xóa thông tin cũ (trừ khi user yêu cầu)
- Nếu feature đã tồn tại => **merge** thông tin mới vào, không ghi đè toàn bộ
- Nếu phát hiện nav_steps **khác** so với hiện tại => ghi cả 2 phiên bản, hỏi user confirm
- Dùng `configs/sitemap_helper.py` để đọc/ghi (đảm bảo format đúng)

### 3.3 Quy trình enrich cho `/cook`
```
1. Đọc sitemap
2. Tìm feature_id tương ứng (hoặc tạo mới nếu chưa có)
3. Chạy cook bình thường
4. Sau khi tạo TC xong:
   a. Cập nhật tc_history: last_cook, tc_count, sheets_url
   b. Nếu phát hiện page/nav mới => thêm vào pages
   c. Nếu phát hiện dependency mới => thêm vào depends_on
   d. Nếu phát hiện impact mới => thêm vào impacts
5. Ghi lại sitemap
```

### 3.4 Quy trình enrich cho `/analyze`
```
1. Đọc sitemap
2. Phân tích requirement documents
3. Sau khi phân tích xong:
   a. Mọi page/screen phát hiện trong docs => thêm vào pages (nếu chưa có)
   b. Mọi feature/function => thêm vào features (nếu chưa có)
   c. Mọi luồng thao tác chung => thêm vào flows
   d. Xác định impacts giữa các feature => thêm vào impact map
4. Ghi lại sitemap
```

---

## 4. Sitemap trong sub-agent prompt

Khi spawn sub-agent cần context sitemap, **PHẢI** truyền dữ liệu sitemap liên quan vào prompt:
- Không truyền toàn bộ file (tốn token) => chỉ truyền phần liên quan
- Format: trích `pages[relevant]` + `features[relevant]` + `flows[relevant]`
- Sub-agent **KHÔNG tự đọc/ghi sitemap** => trả kết quả về main agent để enrich

---

## 5. Validation

- Sau mỗi lần ghi sitemap, **PHẢI** validate bằng `sitemap_helper.validate_sitemap()`
- Nếu validate fail => log warning, giữ bản cũ, báo user
- Các check:
  - YAML syntax hợp lệ
  - Mỗi page có `name` và `nav_steps`
  - Mỗi feature có `page` reference tồn tại trong `pages`
  - Impact `target` tồn tại trong `features` hoặc `pages`
  - Không có circular dependency
