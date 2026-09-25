# GOOD VS. BAD — STYLE & FACTUALITY CALIBRATION

## Example 1: Vague Claims vs. Quantified & Scoped Evidence

### Bad
> *"The system detects attacks extremely effectively and delivers outstanding performance."*  
> (VN: *"Hệ thống có khả năng phát hiện tấn công rất hiệu quả và mang lại hiệu suất vượt trội."*)

**Issues:**
- *"Extremely effective"* lacks an objective metric.
- *"Outstanding"* lacks a comparative baseline.
- Attack vectors, dataset parameters, and testing conditions are omitted.

### Better
> *"Across test dataset X, the system detected Y/Z attack samples in class A, achieving a recall of ... calculated via ... . This result reflects our specific experimental configuration and dataset; it does not provide sufficient basis for generalization to unseen production environments."*  
> (VN: *"Trong bộ kiểm thử X, hệ thống phát hiện Y/Z mẫu thuộc nhóm A, tương ứng với recall ... theo cách tính ... . Kết quả này chỉ phản ánh cấu hình và tập dữ liệu của thí nghiệm; chưa đủ cơ sở để khái quát cho môi trường khác."*)

**Rationale:**
- Explicit target subject;
- Specific dataset and environment parameters;
- Concrete, measurable metric;
- Honest scope boundary and generalization limitations stated.

---

## Example 2: Anthropomorphic / Marketing Fluff vs. Architectural Mechanics

### Bad
> *"AI makes the system much smarter and capable of autonomously defeating complex cyberattacks."*  
> (VN: *"AI giúp hệ thống trở nên thông minh hơn và xử lý các cuộc tấn công phức tạp."*)

**Issues:**
- Anthropomorphic claims (*"smarter"*);
- Marketing hyperbole (*"autonomously defeating"*);
- Zero technical explanation of how decisions are reached.

### Better
> *"The classifier model evaluates incoming traffic samples against predefined feature vectors. Detection efficacy is constrained by extracted feature quality, training distribution coverage, and the chosen classification decision threshold."*  
> (VN: *"Mô hình được sử dụng để phân loại các mẫu lưu lượng theo các đặc trưng đầu vào đã xây dựng. Khả năng phát hiện phụ thuộc vào đặc trưng, dữ liệu huấn luyện và ngưỡng quyết định của mô hình."*)

**Rationale:**
- Explains underlying architectural mechanisms;
- Identifies critical dependencies;
- Bounded and technically verifiable.
