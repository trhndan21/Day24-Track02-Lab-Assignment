# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [ ] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [ ] Backup cũng phải ở trong lãnh thổ VN
- [ ] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [ ] Thu thập consent trước khi dùng data cho AI training
- [ ] Có mechanism để user rút consent (Right to Erasure)
- [ ] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [ ] Có incident response plan
- [ ] Alert tự động khi phát hiện breach
- [ ] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [ ] Đã bổ nhiệm Data Protection Officer
- [ ] DPO có thể liên hệ tại: ___

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | Envelope Encryption (AES-256-GCM) | ✅ Done | Platform Team |
| Audit logging | Structured logging with metadata | ✅ Done | Platform Team |
| Breach detection | Security Scan (Bandit, git-secrets) | ✅ Done | Security Team |

## F. Mô tả Technical Solutions
1. **Audit logging**: 
   - Sử dụng `structlog` hoặc `loguru` để ghi log toàn bộ các request đến API.
   - Mỗi log entry bao gồm: `timestamp`, `user_id`, `role`, `resource_accessed`, `action`, và `result` (Success/Failed).
   - Log được đẩy tập trung về ELK Stack hoặc CloudWatch để phục vụ truy vấn khi có sự cố.

2. **Breach detection**:
   - Sử dụng **Bandit** để quét mã nguồn định kỳ tìm các lỗi bảo mật tiềm ẩn.
   - Sử dụng **git-secrets** và **TruffleHog** để ngăn chặn rò rỉ credential vào git history.
   - Thiết lập cảnh báo (Alerting) khi có số lượng lớn request trả về mã lỗi `403 Forbidden` từ một IP/User trong thời gian ngắn.
