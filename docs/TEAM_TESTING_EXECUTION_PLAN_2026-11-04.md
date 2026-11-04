# KẾ HOẠCH THỰC THI VÀ NGHIỆM THU TESTING | NHÓM 6

**Dự án:** CMC AI Mentor Network  
**Học phần:** Công nghệ phần mềm  
**Điều phối:** Lê Văn Mạnh, trưởng nhóm  
**Ngày lập:** 04/11/2026 (GMT+7)  
**Trạng thái:** Kế hoạch triển khai. KHÔNG coi toàn bộ đầu việc dưới đây là đã hoàn thành.  
**Repository:** https://github.com/levanmanh268/cmc-ai-mentor-network  
**Báo cáo bắt buộc:** MỖI thành viên phải nộp **file Markdown .md** theo mẫu `reports/team/REPORT_TEMPLATE.md`; không dùng tin nhắn "xong" thay báo cáo.

> **Nguyên tắc nghiệm thu:** Chỉ ghi PASS khi có bước chạy, expected/actual và bằng chứng gắn với commit SHA. Test mock không chứng minh gọi Groq thật. Kiểm thử demo không chứng minh AI không hallucinate. Không công khai API key, PII hoặc private logs.

## 1. Hiện trạng được kiểm chứng (snapshot 04/11/2026)

| Mục | Bằng chứng/trạng thái |
| --- | --- |
| Nhánh chính tại thời điểm kiểm tra | `main` = `33819ff51575596c5c17bb2ec79c8a43b0e985c7`. SHA này là **snapshot**, không phải SHA tương lai sau merge. |
| Bảo vệ main | GitHub báo `protected=false`. Cần quản trị viên cấu hình Branch protection/Rulesets và kiểm tra thực tế. |
| PR Testing #161 | https://github.com/levanmanh268/cmc-ai-mentor-network/pull/161 ; **APPROVED, OPEN, chưa merge**, head `d13fa2ac6e3d9422a61f0d5d435a79a33de632fc`; mergeable clean ở thời điểm kiểm tra. |
| PR #161 CI | https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41698114491 ; 5/5 job PASS; Linux 370 pytest + 60 subtests, Windows tương tự, 0 SKIP; Chromium 5 PASS; scoped core line coverage khoảng 97%. |
| PR #161 kiểm toán gói | https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41698114850 ; PASS theo scan tại thời điểm chạy, không bảo đảm không có mọi lỗ hổng. |
| TDD red/green | Red CI: https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41696837055 ; Green CI: https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41697599095 ; kiểm chứng test cho citation đa nguồn. |
| RAG demo | Bộ 31 câu **synthetic/in-sample**, 18 supported/13 no-evidence; các chỉ số demo 18/18 retrieval, 20/20 source mapping, 13/13 refusal không đo đúng ngữ nghĩa toàn cục. |
| Lỗ hổng nghiệm thu | Chưa xác nhận UAT có người thử trên cloud; live Groq; prompt-injection red-team có người chấm; rà soát lịch sử key/revocation; đánh giá gold set độc lập. |
| PR #110 | https://github.com/levanmanh268/cmc-ai-mentor-network/pull/110 vẫn mở. Phải xem có trùng CI evidence với #161 không; KHÔNG merge mù quáng. |

**Mức ưu tiên:** `P0` = chặn nghiệm thu/merge; `P1` = quan trọng cần hoàn tất trước khi demo sản phẩm cuối; `P2` = mở rộng có thể chốt là giới hạn nếu giảng viên không yêu cầu.  
**Trạng thái kết quả:** `PASS / FAIL / SKIPPED / BLOCKED / NOT RUN`. Cấm quy đổi `SKIPPED` hoặc `BLOCKED` thành `PASS`.

## 2. Trình tự công việc chung, không được làm đảo thứ tự

### Giai đoạn A. Chốt code an toàn và quy trình review (P0)
1. **Leader cùng một thành viên độc lập** mở PR #161, kiểm tra phần diff và review history; đặc biệt `app.py`, `rag_engine.py`, `scripts/evaluate_rag.py`, `.github/workflows/ci.yml`. Giữ nguyên nguồn gốc contribution của Dương và các tác giả khác. Trước đó đã APPROVE code, nhưng merge vẫn là một hành động riêng.
2. **Leader và Đăng** kiểm tra PR #110 có chồng lấn #161; nếu đã được thay thế, ghi nhận và đóng đúng lý do sau khi xác minh; không gộp hai PR mà chưa kiểm tra.
3. **Quản trị viên repo** cấu hình `Settings > Branches` hoặc `Rulesets` cho `main`: bắt buộc PR, ít nhất 1 reviewer không phải chính tác giả, chặn merge nếu required checks đỏ/chưa chạy; chọn chính xác tên job đang xuất hiện trong Actions: `test`, `windows-local`, `Chromium browser E2E (real localhost UI)`, 2 job Mermaid, và `pip-audit` nếu workflow này được đưa vào bộ bắt buộc. Bật kiểm tra nhánh đã cập nhật nếu repo hỗ trợ. Chụp screenshot **đã che thông tin nhạy cảm** và thử trên PR an toàn để xác nhận quy tắc có hiệu lực. Chỉ cấu hình khi quyền quản trị cho phép.
4. Kiểm tra head SHA PR #161 không thay đổi so với CI PASS, đã có review phù hợp và GitHub không còn conflicts. Sau đó leader thực hiện **merge #161**, ghi lại SHA merge thực tế. Nếu thay đổi head hoặc main, chạy lại CI thích hợp trước khi merge.

### Giai đoạn B. Xác minh hậu merge trên `main` (P0, issue #164)
1. Chụp `main HEAD SHA` mới và xác nhận PR #161 `merged=true`.
2. Vào GitHub Actions, tìm workflow chạy cho **chính SHA mới trên main**; ghi run URL các job Linux, Windows, Chromium, Mermaid và dependency audit. Các check cũ của nhánh PR không thay thế kết quả hậu merge.
3. Tải JUnit, coverage và artifact có sẵn: ghi `tests/passed/failed/errors/skipped` theo từng job. Nếu xuất hiện SKIP, liệt kê từng case và lý do. Sau merge mới được tuyên bố kết quả thuộc main.
4. Soát các tài liệu `docs/TEST_REPORT.md`, `docs/TRACEABILITY_MATRIX.md`, `docs/TEST_CASES.md`, `docs/RAG_EVALUATION_REPORT.md`, `docs/KNOWN_ISSUES.md`, `docs/UAT_CHECKLIST.md`. Ghi riêng **snapshot cũ** và **bằng chứng mới**, không sửa lịch sử để làm như các bài test cũ chạy ở SHA mới.
5. Nếu CI đỏ: mở bug issue, sửa bằng PR nhỏ, không giấu log. Kết thúc khi các workflow bắt buộc xanh hoặc trạng thái BLOCKED được chứng minh rõ, không tự nhận đã nghiệm thu.

### Giai đoạn C. Tính năng và kiểm thử sản phẩm (P1)
- **Tạo mentor:** issue #165. Cần form thật, validate, tích hợp vào matching/favorites, có test unit + integration + browser. Vì ứng dụng chưa có auth/database, demo ưu tiên **mentor bản nháp theo session**; không ghi dữ liệu mentor mới vào vùng chung của mọi người dùng trên Render.
- **Mentor matching:** issue #84. Verify thứ tự deterministic, điểm biên, filter, dữ liệu thiếu/trùng, mentor mới được tạo; không ngụy tạo khả năng semantic ranking.
- **Browser E2E:** issue #85. Luồng profile, mentor, chat RAG, đổi chế độ, đồng ý gửi dữ liệu; kiểm tra giữa các browser contexts, giảm test flaky; kiểm tra Chrome/Edge thủ công khi có điều kiện.
- **API/LLM:** issue #82. Test 401/403/429/timeout, history, consent, giới hạn, secret masking; dùng fake provider trong CI; live key chỉ nhập trong UI an toàn và **không** nộp key lên GitHub.

### Giai đoạn D. RAG, security, UAT và chất lượng (P1)
- **RAG độc lập:** issue #83, #139, #38. Phúc phối hợp ít nhất 1 người gán nhãn độc lập để tạo >=30 câu gold set (nếu đủ thời gian), có câu đa nguồn, phủ định, nhiễu, mâu thuẫn, injection, ngoài kho. Tách metric: retrieval Recall@k; source/citation mapping; semantic entailment theo từng claim do con người chấm; correctness câu trả lời; refusal. Chỉ số demo/proxy phải có nhãn rõ.
- **Security:** issue #87, #137, #30, #32. Kiểm tra consent, leak trên HEAD/log và **lịch sử Git**, xác minh key từng lộ đã được revoke/rotate bằng chứng private cho leader (không dán secret), dependency audit trên main, prompt injection chỉ trên môi trường được phép. Không dùng dữ liệu cá nhân thực nếu không cần.
- **Human UAT:** issue #88, #35. Có người dùng thực mở ứng dụng công khai, thực hiện từng kịch bản, ghi thiết bị, browser, ngày, expected/actual, PASS/FAIL/BLOCKED, screenshot đã redact. Link public health hoặc mock tests **không** phải bằng chứng live Groq hoạt động.
- **Báo cáo toàn nhóm:** issue #166. Thu từng file `.md` theo mẫu và chốt checklist còn mở, không ép đóng issue có điều kiện nghiệm thu chưa đạt.

## 3. Phân công dự kiến theo năng lực và issue, các thành viên phải tự nhận/đối chiếu

**Nhóm trưởng:** Lê Văn Mạnh. GitHub `@levanmanh268`. Owner tổng thể của #164, #166, #88 và việc bảo vệ `main`. Nhiệm vụ: duyệt PR, điều phối reviewer độc lập, giữ nguyên nguồn gốc đóng góp, hợp nhất an toàn, tổng hợp sign-off và quyết định các blocker P0.

**Hà Văn Dương:** GitHub `@haduong07` (đã xác nhận từ PR #161). Owner chính #165 và #85. Nhiệm vụ: hoàn thành **tạo mentor**, regression UI, trình duyệt thật, session isolation, tài liệu demo. Không tự merge PR của mình; xin người khác review.

**Lê Hải Đăng:** GitHub `@jkdneufewfjn` (theo issue đang được giao, cần thành viên xác nhận lại). #86, #19, phối hợp #164, #131. Nhiệm vụ: CI, JUnit, coverage, test SKIP, tài liệu lệnh tái lập, artifacts, security check gate và hậu merge. Đảm bảo check fail khi test fail/không có bằng chứng.

**Đỗ Văn Cường:** GitHub username cần xác nhận trước khi gán tự động. #84, phối hợp #165. Nhiệm vụ: validation và matching khi mentor mới xuất hiện, boundary/property tests, dữ liệu thiếu/trùng, review logic xếp hạng.

**Dương Tuấn Dũng:** GitHub username cần xác nhận trước khi gán tự động. #87, #137, phối hợp #165. Nhiệm vụ: data-contract, security sanity, quyền riêng tư, lịch sử secret, dependency advisories, không ghi dữ liệu người dùng vào nguồn.

**Nguyễn Văn Phúc:** GitHub username cần xác nhận trước khi gán tự động. #83, #139, #38. Nhiệm vụ: gold set đánh giá RAG độc lập, phân loại hallucination, citation và prompt-injection, viết báo cáo nêu rõ sai sót và độ giới hạn.

> Người thuộc nhóm QA/UAT có thể thử chéo, nhưng **người viết code không tự ký toàn bộ UAT cho chính chức năng mình làm**. Nếu có cộng tác viên ngoài 6 thành viên chính, leader chỉ bổ sung sau khi xác nhận chính thức.

## 4. Lệnh thực thi chuẩn và quy trình GitHub

### Clone và tạo nhánh công việc
```bash
git clone https://github.com/levanmanh268/cmc-ai-mentor-network.git
cd cmc-ai-mentor-network
git switch main
git pull origin main
git switch -c feat/issue-165-mentor-create
```
Đổi tên branch để khớp issue thực tế (ví dụ: `test/issue-83-rag-goldset`). Không commit API key. Không ghi đè nhánh người khác, không push trực tiếp vào `main`.

### Thiết lập môi trường và chạy test
```bash
python -m pip install -r requirements-test.txt
python -m pytest -q -rs
python -m scripts.evaluate_rag
python -m scripts.final_smoke_audit
python -m py_compile app.py rag_engine.py matching_engine.py profile_helpers.py
```
`requirements-test.txt` tồn tại trên nhánh PR #161; **nếu chưa merge**, dùng test requirements tương ứng branch hoặc đợi merge trước khi chạy phiên bản chính thức trên `main`. Coverage phải chạy bằng đúng lệnh trong `.github/workflows/ci.yml`; không trích coverage từ máy khác để gán cho main.

### E2E browser khi liên quan UI
```bash
python -m pip install "pytest-playwright>=0.6,<1"
python -m playwright install chromium
python -m pytest -q e2e/browser_spec.py --browser chromium
```
Với Windows, cài các phụ thuộc đúng README/workflow và ghi rõ các case bị bỏ qua vì môi trường. Nếu test dùng fake API, ghi đó là integration mock, không gọi là live cloud model test.

### Nộp code
1. Mỗi issue: tạo branch riêng, sửa code và test. Nếu là lỗi: đính kèm test tái hiện và chỉ rõ bước red -> green nếu áp dụng.
2. Tạo file **Markdown báo cáo** tại `reports/team/<github_username>_<workstream>_<YYYY-MM-DD>.md` bằng cách copy `reports/team/REPORT_TEMPLATE.md`.
3. Commit cả code, tests và report `.md`; mở PR vào `main`, ghi `Closes #<issue-number>` **chỉ khi đầy đủ điều kiện đóng issue**, nếu còn human UAT thì dùng `Refs #<issue-number>`.
4. Dán link PR, link file `.md` và GitHub Actions vào issue đang làm; tag người review độc lập. Mỗi thành viên chịu trách nhiệm khắc phục nhận xét.
5. Nếu FAIL, đính kèm actual result và traceback đã redact, không xóa bằng chứng. Nếu BLOCKED, ghi thiếu gì, ai có thể tháo blocker và thời điểm dự kiến do nhóm thống nhất (không tự bịa deadline).
6. Chờ reviewer duyệt và CI xanh rồi mới merge. Khi merge, bổ sung merge SHA và hậu merge CI vào báo cáo tổng hợp #164/#166.

## 5. Cách làm RAG gold set để không đánh đồng proxy với chất lượng AI

Mỗi ca có `case_id`, `question`, `expected_source_ids`, `supporting_passages`, `expected_facts`, `should_refuse`, `difficulty`, `reviewer` và `adjudication_notes`. Ít nhất hai người phân biệt người đề xuất với người gán nhãn; nếu bất đồng, ghi rõ hai kết quả trước khi thống nhất. Chia tập in-sample và held-out nếu có đủ dữ liệu, tránh chọn câu chỉ vì mô hình trả lời đúng.

Chấm riêng:
- Retrieval: hit/recall@k, thiếu tài liệu liên quan.
- Citation integrity: trỏ tới nguồn tồn tại và nguồn đúng; **không** suy luận entailment từ việc ID hợp lệ.
- Semantic faithfulness: claim có thực sự được đoạn trích hỗ trợ? Ghi true/false/uncertain và bằng chứng cụ thể.
- Answer correctness: các sự kiện có đúng với đáp án mong đợi, phần nào thiếu hoặc bịa?
- Refusal: thiếu nguồn có từ chối đúng không? Có từ chối quá mức khi nguồn đủ không?
- Prompt injection: phân biệt không thực thi lệnh trong tài liệu với việc kháng tấn công live model. Chỉ kết luận mức đã thử.

Nếu chỉ đánh giá TF-IDF + offline snippets, ghi **offline retrieval regression** thay vì “AI đạt 100% accuracy”.

## 6. Human UAT, kiểm thử bảo mật, dữ liệu nhạy cảm

UAT phải có 2 nhóm: người thao tác thực tế và người ghi/đánh giá kết quả. Test ít nhất Dashboard, tạo/sửa hồ sơ, tìm/ lọc mentor, tạo mentor nếu #165 đã merge, lưu/xóa, grounded RAG positive/negative, đổi mode, khóa consent, xóa lịch sử, refresh/session reset. Ghi URL môi trường, commit/deploy SHA nếu xác định được. Test chức năng AI online chỉ chạy khi có key hợp lệ của người dùng, permission rõ ràng, không ghi prompt/response riêng tư vào artifact công khai.

Các vấn đề có thể chặn nghiệm thu:
- **P0:** credential đang còn hiệu lực bị lộ, không kiểm soát truy cập dữ liệu dùng chung, merge làm CI FAIL, nguy cơ xóa/sửa dữ liệu người khác.
- **P1:** mentor create chỉ có UI mà không ghi vào session/matching; browser E2E fail; RAG bịa dẫn nguồn sai trên tập kiểm thử; UAT tác vụ chính FAIL.
- **P2:** cải thiện thẩm mỹ, benchmark nhỏ, bổ sung công cụ phụ không nằm trong scope bảo vệ.

Secret từng bị lộ trong Git history: chỉ ghi **đã thu hồi/luân phiên key: YES/NO/UNKNOWN** và bằng chứng kiểm tra riêng cho leader. Không chụp màn hình hiển thị key đầy đủ, không dán file .env lên GitHub.

## 7. ĐỊNH DẠNG NỘP BẮT BUỘC: Markdown .md

**Mỗi người nộp đúng định dạng:** `reports/team/<github_username>_<workstream>_<YYYY-MM-DD>.md`. **KHÔNG chỉ nộp** ảnh, tin Zalo “đã xong”, file Word hoặc video. Những thứ đó là minh chứng bổ sung, **không thay thế Markdown**.

File `.md` phải có đủ:
1. Tên, username GitHub, vai trò, ngày thực hiện, issue và PR được giao.
2. Môi trường (OS, Python, framework, URL localhost/cloud) và dữ liệu thử.
3. Baseline SHA, branch HEAD SHA; merge SHA nếu đã merge. Không ghi SHA “ước lượng”.
4. Danh sách test-case ID, từng **Steps / Expected / Actual / Status** và độ ưu tiên.
5. Tổng PASS/FAIL/SKIPPED/BLOCKED/NOT RUN (đếm đúng, tách subtest nếu có).
6. Lệnh đã thực thi, link job log/JUnit/coverage/artifacts, ngày chạy và SHA gắn với bằng chứng.
7. Danh sách bugs, ảnh/trace đã redact, độ nghiêm trọng và issue fix.
8. Các giới hạn: mock/live, offline/cloud, gold-set/demo, security sanity/pentest, human/manual.
9. Kết luận “Ready for review / Needs fixes / Blocked” và người sẽ review.
10. Sau review/merge: ghi thêm review link, merged SHA, main CI mới hoặc nói rõ **PENDING**.

**Mẫu copy:** `reports/team/REPORT_TEMPLATE.md`. Người nào làm nhiều issue có thể một file tổng, nhưng phải có bảng truy vết từng issue và test-case. Ai chưa làm xong vẫn nộp file `.md` với `BLOCKED/NOT RUN`, không báo cáo thành tích chưa có.

## 8. Checklist chốt bảo vệ dành cho trưởng nhóm

- [ ] #161 được merge hợp lệ, có independent review và không làm mất code từ main.
- [ ] Required checks trên main được bảo vệ và có bằng chứng cấu hình / thử nghiệm; nếu chưa làm được phải nói rõ.
- [ ] #164 có main SHA, CI mới, JUnit/coverage và artifact đúng SHA; không mượn CI của PR.
- [ ] #165 tạo mentor hoạt động thật và kiểm thử session/data isolation; nếu chưa hoàn thành, ghi là thiếu.
- [ ] #83 gold set RAG có người chấm độc lập hoặc được ghi NOT RUN nếu chưa có.
- [ ] #87/#137 secret history/revocation được xác nhận, không lộ dữ liệu.
- [ ] #88 human UAT ghi đầy đủ, có actual results.
- [ ] #166 tập hợp báo cáo .md của các thành viên, PR có review và bảng known issues.
- [ ] Tất cả lỗi P0 đã xử lý; P1 còn lại được công khai cho thầy, không giấu.
- [ ] Không tuyên bố “bug-free”, “zero hallucinations”, “NotebookLM parity” hoặc “live Groq PASS” nếu thiếu bằng chứng.

## 9. Các link thao tác chính

- Issues tổng: https://github.com/levanmanh268/cmc-ai-mentor-network/issues
- Pull Requests: https://github.com/levanmanh268/cmc-ai-mentor-network/pulls
- PR #161: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/161
- Post-merge #164: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/164
- Tạo mentor #165: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/165
- Báo cáo MD nhóm #166: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/166
- RAG #83: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/83
- Mentor matching #84: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/84
- Browser E2E #85: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/85
- CI #86: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/86
- Security #87: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/87
- UAT #88: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/88
- Branch protection #131: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/131

**Quy tắc cuối:** Hoàn thành công việc = mã nguồn + test + file báo cáo Markdown + CI evidence theo SHA + review + nghiệm thu phù hợp. Chỉ cần thiếu một thành phần quan trọng thì phải nói đúng trạng thái, không viết “đã hoàn tất 100%”.
