# SOFTWARE TESTING — Bàn giao kiểm thử Nhóm 6

**Dự án:** CMC AI Mentor Network · Môn Công nghệ phần mềm · Nhóm 6  
**Ngày nâng cấp kế hoạch:** 28/10/2026  
**Đối tượng:** ứng dụng gốc Streamlit `app.py`; các portfolio/lab độc lập trong repo không phải một phần của sản phẩm giao diện nhóm.  
**Nguyên tắc:** trạng thái phải gắn với commit SHA + GitHub Actions run. Không tự điền PASS nếu chưa có bằng chứng.

## 1. Test strategy và kỹ thuật

- **Unit / boundary / equivalence partitioning:** đầu vào rỗng, biên độ dài, sai role, lỗi mã HTTP, truy vấn ngoài kho.
- **Integration:** Groq client giả lập (dependency injection), RAG + TF-IDF, mentor matching + lưu hồ sơ.
- **Browser E2E:** dedicated GitHub Actions Chromium headless opens the actual local Streamlit HTTP/WebSocket UI; searches/saves/deletes a mentor and submits offline RAG. This is not the public Render endpoint.\n- **Application E2E in-process:** Streamlit `AppTest` chạy mã giao diện qua nhiều trang, chat, consent, RAG, profile, mentor, favorites. Đây KHÔNG phải Selenium/Playwright hoặc kiểm thử trình duyệt cloud thật.
- **Regression trên CI:** Linux + Windows với pytest/JUnit, compile, offline RAG benchmark, app startup/health, Mermaid CLI hai phiên bản.
- **Bảo mật/riêng tư:** thiếu consent không phát sinh provider call; exception không lộ nội dung secrets; file Markdown vượt kích thước không được index. Đây không phải pentest.
- **Định lượng:** đo scoped source-line coverage với pytest-cov trên Linux; JUnit XML cho cả hai OS. Không đánh đồng line coverage với branch coverage, hiệu năng hay độ chính xác AI.
- **UAT thực tế:** người thử mở link public, điền checklist `UAT_CHECKLIST.md` và ghi thực đo; tình trạng hiện tại vẫn **NOT RUN** nếu chưa có bằng chứng.

## 2. Traceability matrix (test case → requirement → evidence)

| ID | Yêu cầu / mục tiêu | Thao tác hoặc lớp dữ liệu | Expected result | Test automation |
| --- | --- | --- | --- | --- |
| TC-01 | FR Chat offline fail-closed | Không có API key | Không gọi provider; không nhận nhầm là AI online | QG-02, E2E-01 |
| TC-02 | FR Chat validation | History empty/invalid/tool/system/blank | Không gọi provider | QG-01 |
| TC-03 | NFR Privacy chat | Role spoof, previous failed reply, context size | Chỉ system prompt thực và tối đa 16 turns/12K chars | QG-03, QG-04 |
| TC-04 | FR Multi-turn | Fake API trả câu khác nhau, history các lượt | Gửi đúng messages cho provider; response giữ nguyên | QG-05, existing final-defense tests |
| TC-05 | NFR Error handling | API 400,401,403,404,429,500,503 | Thông báo phân loại không tiết lộ secret | QG-06 |
| TC-06 | NFR Error handling | Timeout/Connection/Generic exceptions | Fail-closed, redacted | QG-07 |
| TC-07 | FR Chat | Completion empty/whitespace/None | Không được báo online thành công | QG-08 |
| TC-08 | NFR Input/output bounds | Completion > 12K ký tự | Truncate an toàn | QG-09 |
| TC-09 | FR RAG | Knowledge base trống | No-evidence, không gọi provider | QG-10 |
| TC-10 | FR RAG | Query rỗng / ngoài kho | No-evidence, không gọi provider | QG-11, E2E-01 |
| TC-11 | FR RAG ranking | Query cùng nội dung/k=1 | Kết quả nhất quán, điểm trong [0,1] | QG-12 |
| TC-12 | NFR Hallucination guard | Citation [S0], [S99], trống, pha trộn | Reject id không tồn tại, không được gắn nhãn grounded | QG-13, QG-14 |
| TC-13 | FR RAG fallback | Provider lỗi | Giữ nguồn offline, không hiển thị lỗi nhạy cảm | QG-15 |
| TC-14 | NFR Evidence truth | Response có [S1] nhưng chưa xác thực nghĩa | Chế độ `online-citations-unverified`, không tự nhận entailment | QG-16 |
| TC-15 | FR Profile validation | Trống required / >120, >240 | Hiển thị lỗi, không lưu | QG-17, existing profile AppTest |
| TC-16 | FR Profile boundaries | Giá trị đúng độ dài biên, year cũ | Trim, fallback year, save hợp lệ | QG-18 |
| TC-17 | NFR Session state | Save/reset profile | Xóa matching cache; giữ chat/favorites | QG-19 |
| TC-18 | FR Mentor ranking | Profile cố định | Không trùng ID, top-k, sắp giảm, deterministic | QG-20 |
| TC-19 | FR Mentor filters | Filter không tồn tại | Empty result | QG-21, E2E-06 |
| TC-20 | FR Mentor input safety | top_k âm, 0, lớn, sai kiểu | Kết quả bị giới hạn hợp lệ | QG-22 |
| TC-21 | NFR File safety | Markdown >2 MB | Bỏ qua file lớn | QG-23 |
| TC-22 | FR RAG robustness | Tài liệu toàn punctuation | Không crash / empty vocabulary | QG-24 |
| TC-23 | NFR Source control | Markdown thư mục con | Citation path tương đối, không lộ absolute root | QG-25 |
| TC-24 | FR UI end-to-end | Navigate offline RAG positive+negative+mode switch | Sources, mode đúng, history phân tách | E2E-01 |
| TC-25 | FR UI end-to-end | Profile → Search → Favorite → Rerun → Delete | Lưu/xóa đúng phiên | E2E-02 |
| TC-26 | NFR Consent | Key giả, consent off/on/off | Chỉ có provider call khi đồng ý | E2E-03 |
| TC-27 | NFR Session separation | Hai AppTest instances | Session không chia sẻ profile/favorites | E2E-04 |
| TC-28 | NFR Demo quota | 3 probe fake đã dùng | UI disable probe, không gọi AI thêm | E2E-05 |
| TC-29 | NFR Evidence integrity | JUnit pass/fail, coverage, missing XML | Không giả mạo PASS khi thiếu/fail | `tests/test_testing_report.py` |
| TC-30 | FR Document retrieval benchmark | 9 câu in-domain, 5 out-of-domain | Hit@3 và refusal đúng trên bộ demo | `scripts/evaluate_rag.py` |
| TC-31 | NFR Cross-platform | Python 3.11, Linux/Windows | Pytest và Streamlit health pass | `.github/workflows/ci.yml` |
| TC-32 | NFR Cloud smoke | Public Render health/root | HTTP 200; không suy ra Groq hoạt động | `docs/FINAL_DEFENSE_GATE.md` + manual |
| TC-33 | UAT thực tế | Người thử theo UAT-01..UAT-10 | Ghi người/thiết bị/ngày/actual/issue | `docs/UAT_CHECKLIST.md` — NOT RUN |
| TC-34 | Groq online acceptance | BYOK key thật + explicit consent + model probe | Nội dung provider thật trả về, không 401/403/429 | `docs/FINAL_DEFENSE_GATE.md` — NOT VERIFIED |
| TC-35 | Browser Chromium startup | Load public-facing localhost UI in real Chromium | Dashboard and content appear | `e2e/browser_spec.py::test_browser01_*` |
| TC-36 | Browser Chromium mentor path | Click radio → Search → Save → Delete | Favorites visible and correctly cleared | `e2e/browser_spec.py::test_browser02_*` |
| TC-37 | Browser Chromium RAG | Open AI Assistant → switch to grounded → ask issue | Non-mocked local UI sends question and displays RAG status | `e2e/browser_spec.py::test_browser03_*` |

Ký hiệu `QG-xx` và `E2E-xx` trùng tên hàm `test_qgXX_` / `test_e2eXX_` trong thư mục `tests/`. Một mã có thể gồm nhiều bộ dữ liệu được parameterize, vì vậy tổng số pytest cases sẽ lớn hơn số hàng matrix.

## 3. Cách chạy và xuất bằng chứng ở máy

```bash
python -m pip install -r requirements.txt
python -m pip install "pytest-cov>=6,<8"
python -m pytest -q --junitxml=reports/junit-linux.xml --cov=general_chat --cov=rag_engine --cov=matching_engine --cov=profile_helpers --cov=llm_client --cov=chat_intents --cov=ui_helpers --cov-report=term-missing --cov-report=xml:reports/coverage.xml
python -m scripts.testing_report --junit reports/junit-linux.xml --coverage reports/coverage.xml --output reports/TEST_EXECUTION_REPORT.md
python -m scripts.evaluate_rag
python -m scripts.final_smoke_audit
python -m streamlit run app.py
# Browser E2E in a separate terminal:
python -m pip install "pytest-playwright>=0.6,<1"
python -m playwright install chromium
python -m pytest -q e2e/browser_spec.py --browser chromium --junitxml=reports/junit-browser.xml
```

**CI:** GitHub → Actions → CI → run của commit cần chấm → job `test` / `windows-local` → Artifacts `testing-evidence-linux` (JUnit + coverage XML + báo cáo MD), `testing-evidence-windows` (JUnit), và `testing-evidence-chromium` (JUnit/screenshots/traces nếu test fail). Bằng chứng trong artifacts chỉ hợp lệ cho SHA đó; retention 30 ngày.

Bảng phân loại kết quả khi báo cáo với thầy:

- **PASS:** test đã thực thi và check thành công ở đúng SHA.
- **FAIL:** pytest hoặc điều kiện dự kiến không đạt, có case ID + traceback/issue.
- **SKIPPED:** pytest bỏ qua vì platform/condition, phải thống kê riêng.
- **BLOCKED:** thiếu secret/provider/network/quyền để thực thi; **không** đổi thành PASS.
- **NOT RUN:** chưa có người thực hiện UAT / browser thật.

## 4. Nghiệm thu bằng tay trước buổi bảo vệ

Người kiểm thử: ______ | Ngày giờ: ______ | Git SHA: ______ | Trình duyệt: ______  
Environment: Render URL ______ | Server Live: ______ | Secret không xuất hiện trong ảnh/log: ______

1. Dashboard tải được; thử offline không có key.
2. Hồ sơ hợp lệ/không hợp lệ → Tìm Mentor → bộ lọc → lưu và xóa favorite.
3. RAG hỏi theo tài liệu, mở nguồn; hỏi ngoài kho → no-evidence.
4. Mode đổi General Chat/RAG, hai lịch sử độc lập.
5. Sau khi có credential riêng: bật consent, bấm kiểm tra AI thật, hỏi hai lượt liên tiếp; tắt consent kiểm tra không gọi mới.
6. Dùng trình duyệt khác và phiên mới; đánh giá thực tế session-only, không nhận nhầm persistence.
7. Mỗi FAIL ghi issue, steps-to-reproduce, input (không chứa key), expected, actual, screenshot.

**Giới hạn quan trọng:** fake provider tests chỉ kiểm thử hành vi tích hợp; không kiểm chứng AI ngoài đời, không kiểm chứng semantic faithfulness, không chứng minh đa người dùng/cloud load. Bộ 14 truy vấn RAG là demo in-sample. Không báo cáo `100% bug-free`, `NotebookLM parity` hoặc `Groq online PASS` khi chưa có bằng chứng.
