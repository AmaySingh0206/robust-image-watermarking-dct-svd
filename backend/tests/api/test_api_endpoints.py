import io
import json
import pytest
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.database import init_db

# Ensure DB initialized
init_db()


def create_test_image_bytes(w=512, h=512) -> bytes:
    np.random.seed(42)
    arr = np.random.randint(50, 200, (h, w, 3), dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_capacity_api():
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/watermarks/capacity",
            json={"width": 512, "height": 512, "repetition_factor": 5, "parity_bytes": 32},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_blocks"] == 4096
        assert data["is_feasible"] is True
        assert data["max_payload_bytes"] > 0


def test_embed_and_extract_flow():
    img_bytes = create_test_image_bytes(512, 512)
    payload_msg = "API-VERIFIED-WATERMARK-2026"
    secret_key = "ApiSecurityPassphrase"

    with TestClient(app) as client:
        # 1. Embed Watermark
        embed_res = client.post(
            "/api/v1/watermarks/embed",
            data={
                "payload": payload_msg,
                "secret_key": secret_key,
                "strength_profile": "balanced",
                "repetition_factor": 5,
            },
            files={"file": ("test_image.png", img_bytes, "image/png")},
        )
        assert embed_res.status_code == 200, f"Embed failed: {embed_res.text}"
        embed_data = embed_res.json()
        job_id = embed_data["job_id"]
        manifest = embed_data["recovery_manifest"]
        wm_url = embed_data["watermarked_image_url"]

        assert embed_data["status"] == "completed"
        assert embed_data["metrics"]["psnr_db"] > 35.0

        # Fetch watermarked image file bytes from static mount
        wm_file_res = client.get(wm_url)
        assert wm_file_res.status_code == 200
        wm_bytes = wm_file_res.content

        # 2. Extract Watermark
        ext_res = client.post(
            "/api/v1/watermarks/extract",
            data={
                "secret_key": secret_key,
                "manifest": json.dumps(manifest),
                "ground_truth_message": payload_msg,
            },
            files={"file": ("watermarked.png", wm_bytes, "image/png")},
        )
        assert ext_res.status_code == 200, f"Extract failed: {ext_res.text}"
        ext_data = ext_res.json()
        assert ext_data["success"] is True
        assert ext_data["recovered_message"] == payload_msg

        # 3. Query Job Metadata
        job_res = client.get(f"/api/v1/jobs/{job_id}")
        assert job_res.status_code == 200
        assert job_res.json()["id"] == job_id

        # 4. Download Forensic PDF Report
        pdf_res = client.get(f"/api/v1/reports/{job_id}/download")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert len(pdf_res.content) > 1000  # Non-empty PDF
        assert pdf_res.content.startswith(b"%PDF-")  # Valid PDF signature

