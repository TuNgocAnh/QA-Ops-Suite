# Test Quality Rules

Rules về chất lượng test case, coverage, và expected results.
**Đọc khi**: `/cook`, `/fix`, `/analyze`

---

## 1. Steps Quality

- **Steps must be detailed, clearly step by step**, ensuring the reader can execute them immediately
- Each step must specify: action + data + location on UI
- **Steps describe ACTIONS only** - what the tester does. DO NOT write steps that look like expected results or verification statements
- Good example:
  ```
  1. Open app > Navigate to Login screen
  2. Enter "test@gmail.com" in the Email field
  3. Enter "123456" in the Password field
  4. Tap the "Login" button
  ```
- Bad example - steps look like expected results (DO NOT DO THIS):
  ```
  1. Xác nhận bảng hiển thị đủ 5 cột dữ liệu
  2. Kiểm tra header bảng có màu nền #F2F3F4
  3. Kiểm tra dòng thứ 2 có ngày tạo cũ hơn dòng thứ 1
  ```
  These are verification/expected results, NOT steps. Steps should be actions like "Quan sát bảng danh sách", "Cuộn xuống dòng tiếp theo"...
- Bad example - too vague (DO NOT DO THIS):
  ```
  1. Login with a valid account
  ```

## 2. One Test Objective Per TC

- Each test case tests **ONE specific objective** only
- DO NOT combine multiple scenarios into 1 TC
- TCs must be independent - not dependent on other TC results
- Preconditions can be reused (define shared setups)

## 3. Multi-Result TC Format (MANDATORY)

When a single test description has **multiple expected results to verify**, use the following format:

- **TC_ID count = number of expected results**. Each expected result gets its own TC_ID row
- **Test Description**: merged across all corresponding rows (same description for all rows)
- **Pre-condition**: merged across all corresponding rows (same precondition for all rows)
- **1 step = 1 expected result**. Each row has exactly 1 step and 1 corresponding expected result
- The step describes the **action** to perform; the expected result describes **what to verify**

**Example**: Test description "Kiểm tra hiển thị bảng danh sách S2C - HKD" has 3 results to verify:

| TC_ID | Test Description | Pre-condition | Steps to Perform | Steps Expected Result |
|-------|-----------------|---------------|-------------------|----------------------|
| TC_001 | Kiểm tra hiển thị bảng danh sách S2C - HKD | Đã đăng nhập, truy cập màn hình danh sách S2C - HKD | Quan sát các cột trong bảng danh sách | Bảng hiển thị đủ 5 cột: Mã sổ, Tên sổ, Ngày tạo, Người tạo, Trạng thái |
| TC_002 | Kiểm tra hiển thị bảng danh sách S2C - HKD | Đã đăng nhập, truy cập màn hình danh sách S2C - HKD | Quan sát cuối mỗi dòng trong bảng | Mỗi dòng có icon 3 chấm (more options) ở cuối dòng |
| TC_003 | Kiểm tra hiển thị bảng danh sách S2C - HKD | Đã đăng nhập, truy cập màn hình danh sách S2C - HKD | Quan sát thứ tự sắp xếp các dòng trong bảng | Danh sách được sắp xếp theo ngày tạo giảm dần (mới nhất hiển thị đầu tiên) |

**Key rules**:
- Description & Precondition are **identical** across all rows of the same group (will be visually merged in xlsx)
- Each step is a **concrete action** (quan sát, nhấn, cuộn, nhập...), NOT a verification statement
- Each expected result is **clear and self-explanatory** - no cryptic references like "(BR16)" without context
- DO NOT combine multiple verifications into 1 step/expected result pair

## 4. Negative Test Coverage

- For EVERY positive test case, always consider the corresponding negative scenario
- Example: Positive TC "Login successfully" => Negative: wrong password, empty email, invalid email format, locked account...

## 5. Expected Result Rules

- **DO NOT** write obvious/redundant expected results:
  - "App does not crash" - NO
  - "No lag or jank" - NO
  - "No errors" - NO
  - "App opens successfully" - NO
  - "System works normally" - NO
- Only write expected results that provide **actual testing value**, describing the specific expected outcome
- **DO NOT** include color/hex code checks in expected results (e.g., "Header có màu nền #F2F3F4" - NO)
- **DO NOT** write cryptic references without context (e.g., "Sắp xếp theo BR16" - NO). Write clear descriptions instead (e.g., "Sắp xếp theo ngày tạo giảm dần")
- Good example:
  ```
  - Display message "Login successful"
  - Navigate to Home screen
  - User avatar displays in the top-right corner of the header
  ```

---

## 6. Test Coverage

### 6.1 Coverage Types
- Include: Positive, Negative, Boundary, Edge cases
- Group test cases by scenario/section
- Assign priority: Critical / High / Medium / Low
- **Column Test Type**: Leave blank, DO NOT fill in values (user will fill when needed)
- **Column isAuto**: Leave blank, DO NOT auto-fill values

### 6.2 Four-Part Coverage Framework (When Figma + PRD available)

When writing test cases with both Figma design and PRD/specs, use the following 4-part framework to ensure comprehensive coverage. This is a **section-splitting guideline**, NOT a rigid requirement to have exactly 4 parts - you may combine/split as appropriate for the feature.

**Part 1: UI Display Condition Checks**
- When UI elements show / hide
- Conditional rendering by role/permission
- Loading states, skeleton screens
- Initial state of the interface
- Responsive behavior across devices (if applicable)

**Part 2: UI Object / Data Type Checks**
- All UI elements match Figma (layout, spacing, typography)
- Data types for each input field
- Field constraints (length, format, required/optional)
- Placeholder text, tooltips, icons

**Part 3: Data Display Checks**
- Fetch and render data correctly
- Data formatting (dates, numbers, currency)
- Empty states, no-data scenarios
- Sorting, filtering, pagination
- Data accuracy per business rules

**Part 4: Interaction & Validation Checks**
- All clickable/tappable elements
- Form submissions, error handling
- Input validation rules from PRD
- Edge cases, boundary values
- Business logic workflows
- Error messages, success notifications
- API integration points (if applicable)

> **Note**: This framework is a coverage assurance tool - NOT a rigid template. Adjust as appropriate for each feature. Simple features may not need all 4 parts.

> **DO NOT create test cases for color code verification** (color codes, hex colors, RGB...): Checking exact color codes provides no practical testing value, wastes execution time, and falls under pixel-perfect review scope (designer/dev self-verify). Skip TCs like "Verify the Login button has color #FF5733", "Verify header background is #FFFFFF"...

### 6.3 Conflict Resolution: Specs vs Figma (MANDATORY)

#### Primary Method: Tùy theo command (khi có cả Docs + Figma)

Khi phát hiện xung đột giữa Specs/PRD và Figma design — hành vi **khác nhau theo command**:

**`/analyze`**: Tự động kích hoạt Conflict Resolution Team — xem `.claude/rules/conflict-resolution.md`
- Team gồm: Trinh (Sr. Designer), Hiếu (Sr. PO), Châu (Sr. QA - quyết định cuối cùng)
- Hiển thị chi tiết nội dung tranh luận cho user đọc
- Kết quả ghi vào `{prefix}-conflict-resolution.md`

**`/plan-tc`, `/cook`, `/fix`**: **DỪNG LẠI** hỏi user chọn cách xử lý — xem `.claude/rules/conflict-resolution.md`
- Hiển thị danh sách xung đột, user chọn: theo Docs / theo Figma / chọn từng cái / mở Agent Team
- KHÔNG tự động spawn Agent Team (tránh kết quả không phù hợp context thực tế)

**Mark in output** (cả 2 method): thêm note trong Precondition:
- `[Resolved: Theo Figma]` — nếu quyết định theo design
- `[Resolved: Theo Docs]` — nếu quyết định theo specs
- `[Resolved: Thỏa hiệp]` — nếu compromise
- `[Pending Review]` — nếu cần team thật xác nhận

#### Fallback Method: Mặc định theo Specs (khi team không khả dụng)

Nếu Conflict Resolution Team **không thể kích hoạt** (fail, timeout, hoặc chỉ có 1 nguồn tài liệu):
- **PRIORITIZE Specs/PRD** cho business logic, validation rules, flows
- **PRIORITIZE Figma** cho UI/UX layout, visual design, interaction patterns
- **Notify user** về conflict, bao gồm: Specs nói gì, Figma hiện gì, lý do chọn theo nguồn nào
- **Mark in output**: add note `[Conflict: Specs vs Figma]` trong description hoặc precondition

#### Examples:
- Specs: "Cho phép tối đa 50 ký tự" nhưng Figma hiện field ngắn ~20 ký tự
  - `/analyze`: Agent Team tranh luận, Châu quyết định => theo kết quả
  - `/cook`, `/plan-tc`, `/fix`: Dừng lại hỏi user => user chọn theo Docs/Figma/mở team
  - Fallback: viết TC cho 50 ký tự (Specs), thông báo user
- Specs: "Hiển thị 3 tab: A, B, C" nhưng Figma chỉ có 2 tab: A, B
  - `/analyze`: Agent Team tranh luận, Châu quyết định => theo kết quả
  - `/cook`, `/plan-tc`, `/fix`: Dừng lại hỏi user => user chọn
  - Fallback: viết TC cho 3 tab (Specs), flag cho user

#### Exception:
- Xung đột thuần tuý **visual** (colors, font size, spacing) mà Specs không đề cập => ưu tiên Figma, KHÔNG cần kích hoạt team

### 6.4 Priority Assignment Guidelines

| Priority | When to use | Examples |
|----------|------------|---------|
| **Critical** | Core functionality, blocks entire feature, security issues | Login, payment, data loss |
| **High** | Main functionality, significant UX impact | CRUD operations, main validations, navigation |
| **Medium** | Secondary features, workarounds available | Filter, sort, display formatting |
| **Low** | Minor UI, nice-to-have | Tooltip, hover effect, animation |
