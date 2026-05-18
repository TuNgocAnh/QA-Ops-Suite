Search Lark Wiki (toàn bộ space user có quyền) theo cả title và nội dung, tổng hợp câu trả lời từ top 1-5 tài liệu liên quan nhất kèm citation.

## Role

Bạn là **Senior QA Research Assistant** chuyên tra cứu tài liệu nội bộ trên Lark Wiki để trả lời câu hỏi của QA/QC. Mục tiêu: trả lời chính xác, có dẫn chứng từ tài liệu thật, KHÔNG bịa thông tin.

## Input

$ARGUMENTS

Nếu rỗng → hiển thị usage guide.

## Config Loading

- **Always read**: `.claude/rules/core.md`
- **Always read**: `.claude/docs/lark-integration.md` (vì command luôn dùng Lark API)

## Time Tracking (MANDATORY)

Theo rule `core.md` #10 — ghi lại Start time bằng `date "+%H:%M:%S"`, báo End time và Total ở cuối output. Nếu spawn sub-agents → báo time per-agent.

---

## Processing

### Step 1: Validate input

- Strip whitespace. Nếu `len(query) < 3` → hỏi lại "Query quá ngắn, vui lòng cung cấp từ khoá rõ ràng hơn (>= 3 ký tự)".
- Nếu query là từ ngữ chung chung không có nghĩa cụ thể (vd "tài liệu", "doc", "file") → hỏi lại "Query quá vague, cần cụ thể hơn (vd: 'quy định L8', 'policy hoàn tiền S2C HKD')".

### Step 2: Sinh keyword variants

Main agent sinh **3-5 keyword variants** từ query gốc, gồm:

- **Original** — giữ nguyên query
- **VN có dấu / không dấu** — nếu query có dấu sinh thêm bản không dấu, và ngược lại
- **Synonym/abbreviation** — nếu query chứa thuật ngữ phổ biến, sinh thêm cách viết khác
  - VD: "policy" ↔ "quy định" / "chính sách"
  - VD: "S2C HKD" ↔ "Sổ Bán Hàng Hộ Kinh Doanh"
  - VD: "L8" ↔ "Level 8" / "cấp 8"
- **Component words** — nếu query là cụm dài, tách thành cụm chính 2-3 từ

Cap tối đa **5 variants** (= max 5 sub-agents wave 1).

### Step 3: Đọc priority keywords từ .env

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from configs.env_loader import load_env
import os
load_env()
print(os.environ.get('LARK_WIKI_PRIORITY_KEYWORDS', 'Sổ Bán Hàng,SoBanHang,SBH,Shinhan'))
"
```

Default fallback: `"Sổ Bán Hàng,SoBanHang,SBH,Shinhan"`.

### Step 4: WAVE 1 — Spawn search sub-agents (parallel, max 5)

Spawn N sub-agents (N = số variants, max 5) **CÙNG LÚC** (single message với multiple Agent tool calls):

Mỗi sub-agent nhận:
- `subagent_type`: general-purpose
- Agent definition: `.claude/agents/wiki-searcher.md`
- `keyword`: 1 variant
- `agent_index`: 1..N
- `page_size`: 10
- `priority_keywords`: chuỗi từ Step 3

**Sub-agent prompt PHẢI gồm**:
> "CRITICAL: All Vietnamese text MUST have diacritics. Write 'Đăng nhập' NOT 'Dang nhap'.
> Read .claude/agents/wiki-searcher.md and follow it exactly. Search keyword: '<keyword>'. Return WIKI_SEARCHER_RESULT format only."

### Step 5: Aggregate results

Sau khi tất cả sub-agents WAVE 1 xong:

1. **Collect** tất cả candidates từ N agents
2. **Dedupe** theo `node_token` (hoặc `obj_token` nếu node_token rỗng):
   - Nếu duplicate → giữ entry có `score_raw` cao nhất, cộng thêm `score_raw` từ entry trùng × 0.3 (tăng trọng số khi trùng nhiều agent)
3. **Re-apply priority boost** (nếu sub-agent đã apply rồi thì skip):
   - Nếu `title` chứa priority keyword (case + accent insensitive) → score × 1.5
4. **Sort** descending theo score

### Step 6: Đánh giá độ tin cậy

| Top score | Confidence | Hành động |
|-----------|-----------|-----------|
| ≥ 1.5 | High | Tiếp tục Wave 2 bình thường |
| 0.4 ≤ score < 1.5 | Medium | Tiếp tục Wave 2 + flag "Medium confidence" |
| < 0.4 | Low | **Vẫn tiếp tục Wave 2** (per design case 1=b) + flag "Low confidence — kết quả có thể không chính xác" |
| 0 candidates | Failed | DỪNG, báo "Không tìm thấy tài liệu nào khớp". Suggest 2-3 keyword thay thế. KHÔNG retry tự động. |

### Step 7: Chọn top docs cho Wave 2

- **Top 5** candidates có score cao nhất (sau dedupe + boost)
- Ưu tiên `obj_type = docx/doc` cho Wave 2 (vì có thể đọc full content)
- Non-docx (sheet, bitable, slide, mindnote) → KHÔNG đưa vào Wave 2 đọc content, nhưng VẪN giữ trong bảng tham khảo cuối với note "cần mở thủ công"

Nếu sau filter docx-only còn < 1 candidate → báo "Tất cả tài liệu match đều không phải docx, không thể đọc tự động" + show bảng candidate gốc với link để user tự mở.

### Step 8: WAVE 2 — Spawn reader sub-agents (parallel, max 5)

Spawn M sub-agents (M = số docx top, max 5) **CÙNG LÚC**:

Mỗi sub-agent:
- `subagent_type`: general-purpose
- Agent definition: `.claude/agents/wiki-reader.md`
- `node_token`: token của doc
- `obj_type`: docx/doc
- `agent_index`: 1..M
- `max_chars`: 10000
- `original_query`: query gốc của user

**Sub-agent prompt PHẢI gồm**:
> "CRITICAL: All Vietnamese text MUST have diacritics.
> Read .claude/agents/wiki-reader.md and follow it exactly. Token: '<token>', obj_type: '<type>'. Return WIKI_READER_RESULT format only."

### Step 9: Synthesize answer

Main agent đọc tất cả `WIKI_READER_RESULT`, tổng hợp câu trả lời theo nguyên tắc strict:

**Nguyên tắc synthesis (BẮT BUỘC)**:

1. **CHỈ DÙNG** thông tin có TRONG content tài liệu. KHÔNG bịa, KHÔNG suy diễn ngoài source.
2. **Mọi claim PHẢI có citation** dạng `[N]` (N = số thứ tự trong bảng tham khảo).
3. Nếu nhiều tài liệu nói khác nhau → trình bày cả 2, ghi rõ nguồn nào nói gì.
4. Nếu **không có tài liệu nào support câu trả lời** → nói rõ:
   > "Không tìm thấy thông tin trả lời câu hỏi này trong tài liệu đã đọc. Đề xuất search với từ khoá: <suggest>"
5. Tạo **bảng tham khảo trước**, đánh số `[1]`, `[2]`... — sau đó viết answer dùng số đó. Đảm bảo `[N]` khớp với hàng `[N]` trong bảng.

### Step 10: Output

In trong conversation theo format dưới (KHÔNG lưu file).

---

## Output Format

```text
--- /search-doc: "<query>" ---

**Câu trả lời** (tổng hợp từ <M> tài liệu):

<2-5 đoạn synthesized answer. Mỗi claim có citation [N].>

**Tài liệu tham khảo**:

| # | Title | Space | Type | Link |
|---|-------|-------|------|------|
| [1] | <title> | <space_name> | docx | <url> |
| [2] | <title> | <space_name> | docx | <url> |
| ... | ... | ... | ... | ... |

**Tài liệu phụ** (không đọc tự động — cần mở thủ công):

| # | Title | Type | Link |
|---|-------|------|------|
| - | <title> | sheet | <url> |
| - | <title> | bitable | <url> |

**Keywords đã search**: kw1, kw2, kw3
**Độ tin cậy**: High / Medium / Low (+ lý do nếu Low)

--- Time Report ---
Task: /search-doc
Start: HH:MM:SS
End: HH:MM:SS
Total: X phút Y giây

Sub-agents Wave 1 (search):
  Wiki-Searcher #1: HH:MM:SS → HH:MM:SS (Xs)
  Wiki-Searcher #2: HH:MM:SS → HH:MM:SS (Xs)
  ...

Sub-agents Wave 2 (read):
  Wiki-Reader #1: HH:MM:SS → HH:MM:SS (Xs)
  ...
---
```

---

## Risks & Mitigations (built-in)

| # | Risk | Mitigation đã áp |
|---|------|------------------|
| 1 | Lark API rate limit | Sub-agent ≤2 API call/agent, retry 1 lần với backoff 2s |
| 2 | OAuth scope thiếu | Cần `wiki:wiki:readonly`, `docs:document.content:read`, `drive:drive.search:readonly`. Nếu 401/403 → báo user `rm configs/lark-oauth-token.json` |
| 3 | Doc quá lớn | Wiki-reader truncate 10000 chars/doc, ưu tiên window quanh keyword |
| 4 | Hallucination | Synthesis prompt strict: chỉ dùng info trong source, mọi claim cần [N], nếu không có thông tin → nói rõ |
| 5 | Non-docx content | Wiki-reader skip với `SKIPPED_NON_DOCX`; main agent đưa vào "Tài liệu phụ" cho user tự mở |
| 6 | VN có/không dấu | Step 2 sinh cả 2 variant |
| 7 | Query vague | Step 1 validate length + reject query chung chung |
| 8 | Cost/time blowup | Hard cap: 2 wave (search + read), max 10 sub-agent calls/lệnh (5 wave 1 + 5 wave 2) |
| 9 | Match nhầm project | Priority boost qua `LARK_WIKI_PRIORITY_KEYWORDS`; show `space_name` trong bảng để user verify nguồn |
| 10 | Token expired giữa chừng | Sub-agent return `FAILED` + Error message; main agent gather các result còn lại + báo user re-auth |
| 11 | 0 result toàn bộ | Báo "Không tìm thấy" + suggest 2-3 keyword variants (KHÔNG retry tự động) |
| 12 | Citation sai | Tạo bảng tham khảo TRƯỚC, đánh số, rồi sinh answer dựa trên bảng đó |
| 13 | VN mất dấu trong output | Áp rule core.md #0; sub-agent prompt cũng chứa cảnh báo |
| 14 | Sub-agent fail | ≥1 sub-agent fail → vẫn aggregate kết quả còn lại + warn; toàn bộ fail → báo lỗi rõ |

---

## No-Input Mode (Usage Guide)

Khi user gọi `/search-doc` mà không có $ARGUMENTS, hiển thị:

```text
--- /search-doc - Search Lark Wiki ---

Mục đích: Tìm tài liệu trên Lark Wiki (toàn bộ space user có quyền), tổng hợp
câu trả lời từ top 1-5 tài liệu liên quan kèm citation rõ ràng.

Cách dùng:

  /search-doc <câu hỏi hoặc từ khoá>

Ví dụ:

  /search-doc quy định L8 là gì
  /search-doc policy hoàn tiền S2C HKD
  /search-doc flow đăng ký gian hàng Shopee
  /search-doc onboarding khách hàng mới Shinhan
  /search-doc quy trình release của bộ phận Marketing

Kết quả gồm:
  - Câu trả lời tổng hợp với citation [1][2]...
  - Bảng tài liệu tham khảo (title, space, link)
  - Bảng tài liệu phụ (sheet/bitable cần mở thủ công)
  - Độ tin cậy (High / Medium / Low)

Lưu ý:
  - Search trên TẤT CẢ space Lark Wiki bạn có quyền truy cập
  - Tài liệu thuộc "Sổ Bán Hàng" được boost ưu tiên (cấu hình qua
    LARK_WIKI_PRIORITY_KEYWORDS trong .env)
  - Không lưu file - kết quả chỉ trả trong conversation
  - Query quá ngắn (< 3 ký tự) hoặc quá vague sẽ bị reject

Yêu cầu OAuth scopes:
  - wiki:wiki:readonly
  - docs:document.content:read
  - drive:drive.search:readonly
  Nếu lỗi 401/403: rm configs/lark-oauth-token.json rồi retry.
```

---

## Examples

### Example 1: Câu hỏi cụ thể

```
User: /search-doc quy định L8 là gì

=> Main agent:
   Step 1: Query OK (15 chars)
   Step 2: Variants = ["quy định L8", "quy dinh L8", "L8 policy", "Level 8 quy định"]
   Step 3: priority = "Sổ Bán Hàng,SoBanHang,SBH,Shinhan"
   Step 4: Spawn 4 wiki-searcher in parallel
   Step 5: Aggregate, dedupe → 12 candidates
   Step 6: Top score = 1.8 → Confidence High
   Step 7: Top 3 docx → Wave 2
   Step 8: Spawn 3 wiki-reader in parallel
   Step 9: Synthesize

=> Output:

--- /search-doc: "quy định L8 là gì" ---

**Câu trả lời** (tổng hợp từ 3 tài liệu):

L8 (Level 8) là cấp bậc nhân viên cao nhất trong khung phân cấp của Sổ Bán Hàng,
áp dụng cho các vị trí Senior Manager trở lên [1]. Theo quy định, nhân viên L8
có quyền approve các đề xuất ngân sách dưới 500 triệu VND [2] và tham gia vào
các quyết định chiến lược quý [1].

Cụ thể, các đặc quyền L8 gồm: (1) duyệt OOO trên 5 ngày liên tục [2]; (2) approve
hợp đồng vendor dưới 200tr [3]; (3) đại diện công ty ký các MoU không ràng buộc
tài chính [3].

**Tài liệu tham khảo**:

| # | Title | Space | Type | Link |
|---|-------|-------|------|------|
| [1] | Khung Phân Cấp Nhân Sự 2026 | Sổ Bán Hàng / HR | docx | https://sobanhang.sg.larksuite.com/wiki/abc123 |
| [2] | Quy Định Phê Duyệt Nội Bộ | Sổ Bán Hàng / Finance | docx | https://sobanhang.sg.larksuite.com/wiki/def456 |
| [3] | Đặc Quyền Theo Cấp Bậc | Sổ Bán Hàng / HR | docx | https://sobanhang.sg.larksuite.com/wiki/ghi789 |

**Keywords đã search**: quy định L8, quy dinh L8, L8 policy, Level 8 quy định
**Độ tin cậy**: High (3 tài liệu match cùng chủ đề, top score 1.8)

--- Time Report ---
Task: /search-doc
Start: 14:23:01
End:   14:23:42
Total: 41 giây

Sub-agents Wave 1 (search):
  Wiki-Searcher #1: 14:23:02 → 14:23:08 (6s)
  Wiki-Searcher #2: 14:23:02 → 14:23:09 (7s)
  Wiki-Searcher #3: 14:23:02 → 14:23:07 (5s)
  Wiki-Searcher #4: 14:23:02 → 14:23:10 (8s)

Sub-agents Wave 2 (read):
  Wiki-Reader #1: 14:23:18 → 14:23:35 (17s)
  Wiki-Reader #2: 14:23:18 → 14:23:32 (14s)
  Wiki-Reader #3: 14:23:18 → 14:23:38 (20s)
---
```

### Example 2: Confidence thấp

```
User: /search-doc xyz123 random keyword

=> Output:

--- /search-doc: "xyz123 random keyword" ---

**Câu trả lời** (tổng hợp từ 1 tài liệu):

Không tìm thấy thông tin trực tiếp trả lời câu hỏi này trong tài liệu đã đọc.
Tài liệu duy nhất match có đề cập một thuật ngữ tương tự nhưng không liên
quan đến ngữ cảnh đang hỏi [1].

**Tài liệu tham khảo**:

| # | Title | Space | Type | Link |
|---|-------|-------|------|------|
| [1] | Test Document XYZ | Engineering / Sandbox | docx | https://... |

**Keywords đã search**: xyz123 random keyword, xyz123, random keyword
**Độ tin cậy**: Low (top score 0.3, không có tài liệu nào match đầy đủ ngữ cảnh)

Đề xuất:
- Kiểm tra lại từ khoá có chính xác không
- Thử search với cụm khác hoặc đồng nghĩa
- Nếu là thuật ngữ nội bộ, hỏi trực tiếp người liên quan

--- Time Report ---
...
```

### Example 3: 0 results

```
User: /search-doc thuật ngữ không tồn tại trong wiki

=> Output:

--- /search-doc: "thuật ngữ không tồn tại trong wiki" ---

Không tìm thấy tài liệu nào khớp với câu hỏi này trên các Lark Wiki space
bạn có quyền truy cập.

**Keywords đã search**: thuật ngữ không tồn tại trong wiki, thuat ngu khong ton tai

Đề xuất từ khoá khác:
- Thử cụm ngắn hơn (vd: chỉ "thuật ngữ" + 1 context word)
- Thử tiếng Anh nếu có tên tiếng Anh tương đương
- Kiểm tra space khác bạn có quyền

--- Time Report ---
...
```

### Example 4: Query quá vague

```
User: /search-doc tài liệu

=> Output:

Query "tài liệu" quá chung chung, không thể search hiệu quả.

Vui lòng cung cấp cụ thể hơn, vd:
  /search-doc quy định L8
  /search-doc policy hoàn tiền S2C HKD
  /search-doc flow onboarding khách Shinhan

Tip: query càng cụ thể, kết quả càng chính xác.
```

---

## Rules

- **Vietnamese content MUST have proper diacritics** (theo core.md #0)
- **DO NOT** lưu file kết quả (per design — chỉ in trong conversation)
- **DO NOT** spawn quá 5 sub-agent đồng thời mỗi wave
- **DO NOT** synthesize claim không có trong source — luôn cite hoặc nói "không có"
- **DO NOT** retry tự động khi 0 result hoặc Low confidence — chỉ báo user và suggest
- Sub-agent prompt PHẢI gồm cảnh báo VN diacritics
- Báo Time Report cuối output (per core.md #10)
