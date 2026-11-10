"""CI-only end-to-end verification against real ephemeral PostgreSQL 16.

Checks HTTP, validation, durable write, SSE broadcast and persistence after
ASP.NET process restart. Uses only Python stdlib and synthetic test content.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5060"
HERE = Path(__file__).resolve().parent
APP = HERE / "Group6Live" / "bin" / "Release" / "net10.0"


def request(path: str, *, method="GET", data=None, expected=200):
    headers = {"Accept": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            status = res.status
            raw = res.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read().decode("utf-8")
    assert status == expected, f"{method} {path}: expected {expected}, got {status}: {raw[:300]}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def start(log):
    proc = subprocess.Popen(
        ["dotnet", "Group6Live.dll"],
        cwd=APP,
        env=os.environ.copy(),
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    for _ in range(100):
        if proc.poll() is not None:
            raise RuntimeError(f"ASP.NET exited early with status {proc.returncode}")
        try:
            live = request("/health/live")
            if live.get("status") == "running":
                return proc
        except (urllib.error.URLError, TimeoutError, ConnectionError, AssertionError):
            time.sleep(0.25)
    raise RuntimeError("ASP.NET never started listening")


def stop(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=12)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=6)


def main():
    if not os.environ.get("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL must be configured for real integration")
    tests = []
    with (HERE / "e2e-server.log").open("wb") as server_log:
        proc = start(server_log)
        try:
            assert request("/health/ready") == {"status": "ready", "database": "postgresql"}
            tests.append("ready_postgresql")
            status = request("/api/status")
            assert status["online"] and status["database"] == "postgresql"
            tests.append("database_status")
            mentors = request("/api/mentors")
            assert len(mentors) >= 3
            assert all(m["name"].startswith("Mentor Demo") for m in mentors)
            tests.append("postgres_mentor_seed")

            initial = request("/api/requests")
            assert isinstance(initial, list)
            item = request("/api/requests", method="POST", expected=201, data={
                "nickname": "Sinh viên thử nghiệm",
                "topic": "RAG",
                "message": "Tôi muốn học xây dựng hệ thống truy xuất tài liệu."
            })
            assert item["id"] > 0
            tests.append("postgres_parameterized_insert")

            latest = request("/api/requests")
            assert any(x["id"] == item["id"] for x in latest)
            tests.append("postgres_read_after_write")

            invalid = request("/api/requests", method="POST", expected=400, data={
                "nickname": "Demo", "topic": "untrusted", "message": "Nội dung hợp lệ"
            })
            assert "error" in invalid
            tests.append("input_validation_bad_request")

            stream_req = urllib.request.Request(BASE + "/api/events")
            with urllib.request.urlopen(stream_req, timeout=12) as stream:
                line = stream.readline().decode("utf-8")
                assert line.startswith(": connected"), line
                item2 = request("/api/requests", method="POST", expected=201, data={
                    "nickname": "Sinh viên B", "topic": "Mentor",
                    "message": "Tìm mentor để làm phần mềm nhóm."
                })
                lines = []
                for _ in range(7):
                    next_line = stream.readline().decode("utf-8").strip()
                    lines.append(next_line)
                    if next_line == "event: changed":
                        break
                assert "event: changed" in lines, f"No realtime event: {lines}"
                tests.append("sse_realtime_after_commit")

        finally:
            stop(proc)

        proc = start(server_log)
        try:
            after_restart = request("/api/requests")
            assert any(x["id"] == item["id"] for x in after_restart)
            assert any(x["id"] == item2["id"] for x in after_restart)
            tests.append("postgres_persistence_after_process_restart")
        finally:
            stop(proc)
    evidence = {"status": "PASS", "storage": "real-postgresql", "cases": tests, "count": len(tests)}
    (HERE / "e2e-result.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == "__main__":
    main()
