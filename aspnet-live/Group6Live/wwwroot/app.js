"use strict";
const $ = (id) => document.getElementById(id);
const state = { ready: false, streaming: false, syncing: false };
const htmlLabels = { AI: "AI / ML", RAG: "RAG / LLM", Mentor: "Mentor", Career: "Hướng nghiệp", Other: "Khác" };

async function api(path, options = {}) {
  const response = await fetch(path, { cache: "no-store", ...options });
  let body;
  try { body = await response.json(); }
  catch { body = { error: "Phản hồi từ server không hợp lệ." }; }
  if (!response.ok) throw new Error(body.error || "Server đang không khả dụng.");
  return body;
}
function text(tag, value, css) {
  const el = document.createElement(tag);
  el.textContent = value ?? "";
  if (css) el.className = css;
  return el;
}
function setStatus(ok, message) {
  state.ready = ok;
  $("connection-dot").className = "dot " + (ok ? "connected" : "offline");
  $("connection-text").textContent = message;
  $("unavailable").classList.toggle("hidden", ok);
  $("submit").disabled = !ok;
}
function friendlyTime(date) {
  const value = new Date(date);
  return Number.isNaN(value.getTime()) ? "Chưa rõ thời gian" :
    new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }).format(value);
}
function renderPosts(rows) {
  const host = $("post-list");
  host.replaceChildren();
  if (!Array.isArray(rows) || !rows.length) {
    host.append(text("div", "Chưa có yêu cầu. Hãy gửi bài đầu tiên!", "placeholder"));
    return;
  }
  for (const row of rows) {
    const card = text("article", "", "post");
    const head = text("div", "", "post-head");
    head.append(text("strong", row.nickname || "Người học ẩn danh"));
    head.append(text("span", htmlLabels[row.topic] || "Khác", "topic"));
    card.append(head);
    card.append(text("p", row.message));
    card.append(text("small", friendlyTime(row.createdAt), "post-time"));
    host.append(card);
  }
}
function renderMentors(rows) {
  const host = $("mentor-list");
  host.replaceChildren();
  if (!Array.isArray(rows) || !rows.length) {
    host.append(text("div", "Chưa có dữ liệu mentor.", "placeholder"));
    return;
  }
  for (const m of rows) {
    const card = text("article", "", "mentor");
    const initial = String(m.name || "M").trim().charAt(0).toUpperCase();
    card.append(text("div", initial, "avatar"));
    card.append(text("h3", m.name));
    card.append(text("span", m.field, "topic"));
    card.append(text("p", m.bio));
    host.append(card);
  }
}
async function refresh() {
  if (state.syncing) return;
  state.syncing = true;
  try {
    const [status, requests, mentors] = await Promise.all([
      api("/api/status"), api("/api/requests"), api("/api/mentors")
    ]);
    setStatus(true, state.streaming ? "PostgreSQL đã kết nối · realtime" : "PostgreSQL đã kết nối");
    renderPosts(requests);
    renderMentors(mentors);
    $("request-count").textContent = String(status.requests ?? requests.length);
    $("mentor-count").textContent = String(mentors.length);
    $("refreshed-at").textContent = "Đồng bộ lần cuối: " + new Intl.DateTimeFormat("vi-VN", {timeStyle:"medium"}).format(new Date());
  } catch {
    setStatus(false, "Database chưa sẵn sàng");
    $("post-list").replaceChildren(text("div", "Không thể tải dữ liệu. Kết nối sẽ được thử lại.", "placeholder"));
    $("mentor-list").replaceChildren(text("div", "Database chưa sẵn sàng.", "placeholder"));
    $("request-count").textContent = "⋯";
    $("mentor-count").textContent = "⋯";
  } finally {
    state.syncing = false;
  }
}
$("message").addEventListener("input", (e) => {
  $("length").textContent = e.target.value.length + " / 380";
});
$("post-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.ready) return;
  const values = {
    nickname: $("nickname").value,
    topic: $("topic").value,
    message: $("message").value
  };
  if (values.message.trim().length < 5 || values.message.trim().length > 380) {
    $("form-result").textContent = "Nội dung cần từ 5 đến 380 ký tự.";
    return;
  }
  $("submit").disabled = true;
  $("form-result").textContent = "Đang lưu vào PostgreSQL...";
  try {
    await api("/api/requests", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values)
    });
    $("message").value = "";
    $("length").textContent = "0 / 380";
    $("form-result").textContent = "Đã lưu thành công! Các cửa sổ đang mở sẽ được cập nhật.";
    await refresh();
  } catch (error) {
    $("form-result").textContent = error.message || "Có lỗi. Vui lòng thử lại.";
  } finally { $("submit").disabled = !state.ready; }
});
if (window.EventSource) {
  const stream = new EventSource("/api/events");
  stream.addEventListener("open", () => { state.streaming = true; if (state.ready) setStatus(true, "PostgreSQL đã kết nối · realtime"); });
  stream.addEventListener("changed", () => { void refresh(); });
  stream.addEventListener("error", () => { state.streaming = false; });
}
void refresh();
window.setInterval(() => { void refresh(); }, 12000);
