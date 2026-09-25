# TECHNICAL WRITING RULES

## Anatomy of a Rigorous Technical Sentence

A high-quality technical sentence answers as many of the following as applicable:
- **Entity**: What component/system is involved?
- **Mechanism / Action**: How does it operate?
- **Precondition / Configuration**: Under what parameters?
- **Outcome / Metric**: What occurred?
- **Boundary / Limitation**: What is the scope?

**Example:**
`The architecture utilizes Sysmon Event ID 1 to ingest process creation telemetry on Windows hosts. In this test environment, log streams were forwarded to Splunk via the Universal Forwarder agent.`  
(VN: `Hệ thống sử dụng Sysmon Event ID 1 để thu thập sự kiện tạo tiến trình trên Windows. Trong thí nghiệm này, dữ liệu được chuyển về Splunk thông qua Universal Forwarder.`)

## Forbidden Unhedged Superlatives

Prohibited terms without quantitative evidence:
- *"extremely fast"*, *"superior"*, *"optimal"*;
- *"guarantees"*, *"ensures total security"*;
- *"always"*, *"completely"*, *"flawless"*.

## Calibrated Hedging

Employ calibrated hedging when conditions or scopes dictate:
- *"Within our experimental setup..."* (VN: *"trong phạm vi thử nghiệm"*);
- *"Under condition X..."* (VN: *"trong điều kiện X"*);
- *"Contingent upon..."* (VN: *"phụ thuộc vào"*);
- *"Our empirical observations indicate..."* (VN: *"kết quả cho thấy"*);
- *"Insufficient data to conclude..."* (VN: *"chưa đủ cơ sở để kết luận"*).

Do not hedge unambiguous empirical facts. State established facts directly.
