import json
import subprocess
import sys
from pathlib import Path

# Run from an isolated checkout/venv with:
#   HEADROOM_TELEMETRY=off /tmp/headroom-venv/bin/python bench_headroom.py
# Requires the Headroom source checkout or installed package to be importable.

sys.path.insert(0, "/tmp/headroom-inspect")
from headroom.compression import compress  # noqa: E402


def token_count(text: str) -> int:
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def build_samples() -> dict[str, str]:
    samples: dict[str, str] = {}

    rows = []
    for i in range(200):
        rows.append(
            {
                "id": f"CDL-{1000 + i}",
                "capture_id": f"cap_20260608_{i:04d}",
                "status": "complete" if i % 5 else "failed",
                "failed_step": "transcribe" if i % 17 == 0 else None,
                "workflow_run_id": f"wr_{i:08x}_a165595878d3bc64c5381dfef6813128",
                "notes": (
                    "Snowden Quick Capture audio audit row with survey field note metadata, "
                    "GNSS RTK 12D TBC references, repeated operational detail. "
                    * (2 + (i % 4))
                ),
                "created_at": "2026-06-08T12:34:56Z",
            }
        )
    samples["json_d1_results"] = json.dumps({"results": rows}, indent=2)

    samples["worker_logs"] = "\n".join(
        f"2026-06-08T12:{i % 60:02d}:00Z [INFO] request_id=req_{i:05d} "
        f"route=/api/quick-capture/audio capture_id=cap_{i:04d} "
        f"status={'500 ERROR AiError 5006 Type mismatch of /audio' if i in (55, 102, 177) else '200 OK'} "
        f"duration_ms={120 + i % 80} user=field@snowden"
        for i in range(260)
    )

    code_path = Path("/home/mike/.hermes/hermes-agent/agent/context_compressor.py")
    samples["hermes_context_compressor_code"] = code_path.read_text(encoding="utf-8", errors="replace")[:65000]

    transcript = subprocess.check_output(
        [
            "python3",
            "/home/mike/.hermes/profiles/snowden/skills/media/youtube-content/scripts/fetch_transcript.py",
            "https://youtu.be/UOWSHg18cL0?si=NrGTeE3OgW_40NtS",
            "--timestamps",
        ],
        text=True,
        timeout=120,
    )
    samples["headroom_video_transcript"] = transcript[:70000]

    samples["browser_snapshot_like"] = "\n".join(
        f"[ref @e{i}] link/button text='Snowden dashboard item {i}' "
        f"aria='Open deliverable CDL-{700 + i}' details='long repeated navigation and "
        "CSS classes card border text muted action dropdown status priority owner updated timestamp'"
        for i in range(450)
    )

    return samples


def main() -> None:
    output = []
    for name, content in build_samples().items():
        before = token_count(content)
        try:
            result = compress(content)
            compressed = getattr(result, "compressed", str(result))
            after = token_count(compressed)
            output.append(
                {
                    "sample": name,
                    "chars_before": len(content),
                    "chars_after": len(compressed),
                    "tokens_before_est": before,
                    "tokens_after_est": after,
                    "tokens_saved_est": before - after,
                    "savings_pct_est": round((before - after) / before * 100, 1) if before else 0,
                    "content_type": str(getattr(result, "content_type", None)),
                    "handler_used": str(getattr(result, "handler_used", None)),
                    "ccr_key_present": bool(getattr(result, "ccr_key", None)),
                    "sample_compressed_prefix": compressed[:500].replace("\n", "\\n"),
                }
            )
        except Exception as exc:  # keep benchmark failure evidence in results
            output.append(
                {
                    "sample": name,
                    "error": repr(exc),
                    "tokens_before_est": before,
                    "chars_before": len(content),
                }
            )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
