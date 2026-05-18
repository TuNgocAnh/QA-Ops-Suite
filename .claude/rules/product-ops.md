# Product Ops Rules

Rules về Product Ops: SLA, health metrics, release readiness, triage, risk assessment.
**Đọc khi**: `/sla`, `/health`, `/release-check`, `/triage`, `/risk`

---

## 1. SLA Defaults

### SLA Targets (mặc định, user có thể override)

| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| P1 - Critical | 15 phút | 4 giờ |
| P2 - High | 1 giờ | 24 giờ |
| P3 - Medium | 4 giờ | 72 giờ |
| P4 - Low | 24 giờ | 1 tuần |

### Priority Mapping

Khi dữ liệu dùng tên khác => tự động map:

| Input | Maps to |
|-------|---------|
| Critical, Blocker, Urgent, S1 | P1 |
| High, Major, S2 | P2 |
| Medium, Normal, Moderate, S3 | P3 |
| Low, Minor, Trivial, S4, Cosmetic | P4 |

---

## 2. Health Metrics Thresholds

### Quality

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Bug Escape Rate | <5% | 5-15% | >15% |
| Regression Rate | <3% | 3-8% | >8% |
| Critical Bugs (Open P1/P2) | 0 | 1-2 | >2 |

### Customer

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Customer-Reported Bug Ratio | <20% | 20-40% | >40% |
| Repeat Issue Rate | <5% | 5-10% | >10% |

### Testing

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Test Coverage Rate | >80% | 60-80% | <60% |
| Test Execution Rate | >95% | 80-95% | <80% |
| Test Pass Rate | >95% | 85-95% | <85% |

### Velocity

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Hotfix Rate | <10% | 10-25% | >25% |

---

## 3. Release Readiness Gates

### Critical Gates (FAIL => NO-GO)
- **G1 - Test Completion**: Execution rate >= 95%
- **G2 - Test Pass Rate**: Pass rate >= 95%
- **G3 - Critical Bugs**: 0 P1/P2 open

### Important Gates (FAIL => CONDITIONAL GO possible)
- **G4 - High Bugs**: Tất cả P3 triaged (workaround hoặc accepted)
- **G5 - Regression**: Regression suite pass = 100%

### Advisory Gates (FAIL => noted, không block)
- **G6 - Rollback Plan**: Documented
- **G7 - Release Notes**: Reviewed
- **G8 - Sign-off**: QA Lead + PM + Tech Lead approved

### Verdict Logic
```
IF any G1/G2/G3 FAIL => NO-GO
ELIF confidence >= 70% AND no P1/P2 open => CONDITIONAL GO
ELSE => NO-GO

Confidence = (PASS gates / (Total - N/A)) x 100%
```

---

## 4. RICE Scoring Framework

| Factor | Scale | Hướng dẫn |
|--------|-------|-----------|
| **Reach** | Số user bị ảnh hưởng | Estimate từ description, reports |
| **Impact** | 3=Massive, 2=High, 1=Medium, 0.5=Low | Dựa trên mức ảnh hưởng workflow |
| **Confidence** | 100%=High, 80%=Medium, 50%=Low | Mức tự tin về Reach + Impact |
| **Effort** | Person-days | Estimate complexity sửa lỗi |

**Formula**: `RICE = (Reach x Impact x Confidence) / Effort`

---

## 5. Risk Matrix

### Scoring
- **Likelihood**: 1 (Rare) - 2 (Unlikely) - 3 (Possible) - 4 (Likely) - 5 (Almost Certain)
- **Impact**: 1 (Negligible) - 2 (Minor) - 3 (Moderate) - 4 (Major) - 5 (Catastrophic)
- **Risk Score** = Likelihood x Impact

### Risk Levels
| Score | Level | Action |
|-------|-------|--------|
| 1-4 | Low | Standard testing |
| 5-9 | Medium | Additional coverage, peer review |
| 10-15 | High | Exploratory testing, staged rollout, contingency plan |
| 16-25 | Critical | Full regression, canary deploy, rollback plan mandatory |

---

## 6. Bug Classification

### Severity

| Severity | Tiêu chí | Response | Resolution |
|----------|---------|----------|------------|
| P1 - Critical | System down, data loss, security breach | 15 phút | 4 giờ |
| P2 - High | Major feature broken, no workaround | 1 giờ | 24 giờ |
| P3 - Medium | Feature impaired, workaround exists | 4 giờ | 72 giờ |
| P4 - Low | Minor, cosmetic | 24 giờ | 1 tuần |

### Bug Types

| Type | Code | Mô tả |
|------|------|--------|
| Functional | `FUNC` | Logic, flow, business rule |
| UI/UX | `UI` | Display, layout, interaction |
| Performance | `PERF` | Slow, timeout, memory |
| Data | `DATA` | Loss, corruption, calculation |
| Security | `SEC` | Auth, authorization, exposure |
| Integration | `INT` | API, third-party, cross-module |
| Regression | `REG` | Previously fixed bug reappeared |

---

## 7. Output Rules

### Product Ops commands output to:
- **Reports**: `results/<context-name>/` as `.md` files
- **Data tables**: `.xlsx` files (optional, for substantial data)
- Upload follows same priority: Lark > Google > local only

### Context naming:
- Nếu user cung cấp feature/sprint name => dùng làm context name
- Nếu không => dùng date-based: `ops-<YYYY-MM-DD>`
- Directory names: lowercase, hyphens (e.g., `sprint-15`, `payment-module`)

### Branding:
- All reports: **Created by: QA Ops Suite**

---

## 8. Config Loading

Product Ops commands đọc:

| Command | core.md | product-ops.md | sitemap.md |
|---------|---------|----------------|------------|
| `/sla` | Yes | Yes | On-demand |
| `/health` | Yes | Yes | On-demand |
| `/release-check` | Yes | Yes | On-demand |
| `/triage` | Yes | Yes | Yes |
| `/risk` | Yes | Yes | Yes |
