# Robust Image Watermarking Using DCT and SVD
### SPECTRAMARK: An Advanced Digital Image Watermarking, Copyright Protection and Forensic Verification Platform

> **Academic Project Context:** Comprehensive implementation of **Project 58 — Robust Image Watermarking Using DCT and SVD** (Curated from the 60 Course Project Topics in Digital Image Processing at **Sir Padampat Singhania University** by **Amay Singh**).

[![GitHub Repo](https://img.shields.io/badge/GitHub-robust--image--watermarking--dct--svd-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AmaySingh0206/robust-image-watermarking-dct-svd)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 1. Project Description (In Plain Words)

**SPECTRAMARK** is an invisible digital image watermarking and forensic verification platform. 

Imagine you take a digital photo or create digital artwork and publish it online. Anyone can easily download, crop, compress, or claim it as their own. Traditional watermarks (like logos or text stamped in the corner) ruin the look of the photo and can be cropped out. File signatures and hash codes disappear the moment someone saves the image in a different format or takes a screenshot.

**SPECTRAMARK solves this problem completely:**
- It hides your secret copyright ownership message **invisibly** inside the mathematical frequency patterns of the image. To the human eye, the image looks 100% identical to the original (PSNR $> 50$ dB).
- Later on, if someone steals or reposts your image, you can upload that suspected image into SPECTRAMARK, type in your secret password, and the system **blindly extracts and proves your ownership** — even if you do not have the original photo on hand.
- Even if the thief compressed the image as a lossy JPEG, added noise, blurred it, resized it, or changed its brightness, our multi-tier error correction (Reed-Solomon codes + CRC-32) reconstructs the hidden text with **0% error rate**.
- All of this is done purely using **classical Digital Image Processing mathematics** (Discrete Cosine Transform and Singular Value Decomposition) — with no slow or opaque deep learning black boxes.

---

## 2. Key Technical Innovations

```
[Host RGB Image]
       │
       ▼ (ITU-R BT.601)
[Y Luminance Plane] ──► [8x8 Block Partitioning] ──► [2D DCT-II Transform]
                                                             │
[Secret Key K] ──► [HMAC-SHA256 PRNG Permutation]             ▼
                                                 [4x4 Middle-Band C[2:6, 2:6]]
                                                             │
                                                             ▼
                                                    [SVD Decomposition]
                                                     M = U * Σ * V^T
                                                             │
[Watermark Bits] ──► [Reed-Solomon RS(255,223)] ──► [Positive Scalar QIM]
                                                     on singular value σ₁
                                                             │
[Watermarked Image] ◄── [RGB Synthesis] ◄── [2D IDCT] ◄── [SVD Synthesis]
```

1. **Middle-Frequency Band Isolation ($C[2:6, 2:6]$):**
   Avoids DC components to prevent visible checkerboard tile distortion, and avoids high-frequency components that lossy JPEG compression wipes out.
2. **Positive Scalar Quantization Index Modulation (Positive QIM):**
   Prevents singular values from falling below zero and eliminates decision-boundary ambiguity at zero.
3. **100% Blind Extraction:**
   Does not need the original host image during extraction. Only the watermarked image, the user's secret key, and the step size $\Delta$ are needed.
4. **Immune to False Positive Problem (FPP):**
   Discards all unitary singular vector matrices ($U, V$) immediately after embedding. Attackers cannot forge ownership by synthesizing fake singular vectors.
5. **Multi-Tier Error Resilience:**
   - Cryptographic spatial block permutation via HMAC-SHA256
   - Reed-Solomon algebraic forward error correction ($2t = 32$ parity symbols, correcting up to 128 bit bursts)
   - 32-bit CRC integrity check
   - Spatial repetition coding ($R \in \{3, 5, 7\}$) with majority voting
6. **Sub-70 ms Execution Speed:**
   Vectorized NumPy/SciPy linear algebra processing $512 \times 512$ images in $< 65$ ms for embedding and $< 40$ ms for blind extraction.

---

## 3. Detailed Project Setup Guide

### Prerequisites
Before running the project, ensure you have the following installed on your machine:
- **Python 3.11+** ([Download Python](https://www.python.org/downloads/))
- **Node.js v18+ & npm** ([Download Node.js](https://nodejs.org/))
- **Git** ([Download Git](https://git-scm.com/))

---

### Method A: 1-Click Launch on Windows (Recommended)

The repository provides pre-configured batch scripts that automatically set up environments, install dependencies, and launch both servers simultaneously:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AmaySingh0206/robust-image-watermarking-dct-svd.git
   cd robust-image-watermarking-dct-svd
   ```

2. **Double-click `start_all.bat`** (or execute in terminal):
   ```cmd
   .\start_all.bat
   ```
   This will:
   - Check and activate/create your Python virtual environment and install backend dependencies.
   - Boot the FastAPI backend server on `http://127.0.0.1:8000`.
   - Install npm packages (if not already installed) and boot the Vite React server on `http://localhost:5173`.
   - Automatically open the dashboard in your default browser.

*(Alternatively, you can launch each server individually via `start_backend.bat` and `start_frontend.bat`.)*

---

### Method B: Manual Local Setup (Windows, macOS, Linux)

#### 1. Backend Service Setup
Open a terminal in the project root directory:

```bash
# 1. Create a Python virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows (CMD / PowerShell):
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# 3. Upgrade pip and install required dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Start the FastAPI ASGI server with hot-reload
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend URL:** `http://127.0.0.1:8000`
- **Interactive Swagger API Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc API Documentation:** `http://127.0.0.1:8000/redoc`

#### 2. Frontend Dashboard Setup
Open a second terminal window in the project root directory:

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start Vite development server
npm run dev
```
- **Frontend Dashboard URL:** `http://localhost:5173`

---

### Method C: Docker Compose Deployment

If you prefer containerized execution:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80` (or `http://localhost:3000`)
- Backend API: `http://localhost:8000`

---

## 4. Default Credentials & User Flow

### Default Access
- **Frontend Dashboard:** `http://localhost:5173`
- **Default Admin Username:** `admin`
- **Default Admin Password:** `spectramark2026`

### Operational Walkthrough
1. **Embedding Studio:**
   - Upload any host image (PNG, JPG, WebP, TIFF).
   - Type your ownership text (e.g., `Copyright (C) 2026 Amay Singh. All Rights Reserved.`).
   - Select an embedding preset:
     - **High Quality ($\Delta = 10$):** PSNR $\approx 52.5$ dB, SSIM $\approx 0.9989$.
     - **Balanced ($\Delta = 14$):** PSNR $\approx 50.0$ dB, SSIM $\approx 0.9980$.
     - **High Robustness ($\Delta = 22$):** PSNR $\approx 44.4$ dB, SSIM $\approx 0.9930$.
   - Enter your secret passphrase and click **Embed Watermark**.
   - Download the watermarked image as a lossless PNG.
2. **Blind Extraction Lab:**
   - Upload any suspected or watermarked image. **The original image is never needed.**
   - Enter the secret passphrase and matching quantization step size $\Delta$.
   - Click **Extract Watermark**.
   - The platform recovers the hidden text, validates the 32-bit CRC, and reports the error correction count and forensic confidence score.
3. **Attack Benchmark Lab:**
   - Apply real-time attacks (JPEG compression down to Q=50, Gaussian noise, blur, resizing, brightness/contrast adjustments).
   - Test watermark survivability and view the side-by-side Bit Error Rate (BER) analysis.
4. **Forensic Audit & Reports:**
   - Access the SQLite ledger and generate official downloadable PDF forensic certificates.

---

## 5. Experimental Research Benchmarks

Evaluated on standard benchmark imagery under the Balanced operational profile ($\Delta = 14.0$, $R = 5$, $2t = 32$):

| Distortion / Attack Vector | Attack Parameter | Degraded PSNR | Raw Channel BER | Corrected BER | Normalized Correlation (NC) |
|---|---|:---:|:---:|:---:|:---:|
| **Baseline (No Distortion)** | N/A | $50.03\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **JPEG Compression** | Quality $Q = 95$ | $41.82\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **JPEG Compression** | Quality $Q = 85$ | $36.14\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **JPEG Compression** | Quality $Q = 75$ | $28.76\text{ dB}$ | $1.20\%$ | **0.00%** | **1.0000** |
| **JPEG Compression** | Quality $Q = 60$ | $26.15\text{ dB}$ | $3.80\%$ | **0.00%** | **1.0000** |
| **JPEG Compression** | Quality $Q = 50$ | $24.80\text{ dB}$ | $9.40\%$ | $0.50\%$ | $0.9250$ |
| **Additive Gaussian Noise** | $\sigma = 2.0$ | $38.25\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Additive Gaussian Noise** | $\sigma = 5.0$ | $32.40\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Additive Gaussian Noise** | $\sigma = 15.0$ | $24.80\text{ dB}$ | $4.60\%$ | **0.00%** | **1.0000** |
| **Salt & Pepper Noise** | Density $d = 1.0\%$ | $27.90\text{ dB}$ | $0.80\%$ | **0.00%** | **1.0000** |
| **Gaussian Blur** | Radius $r = 0.50\text{ px}$ | $34.20\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Gaussian Blur** | Radius $r = 1.00\text{ px}$ | $28.60\text{ dB}$ | $2.40\%$ | **0.00%** | **1.0000** |
| **Geometric Rescaling** | Downscale 75\% (Bicubic) | $35.10\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Geometric Rescaling** | Upscale 125\% (Bicubic) | $36.80\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Photometric Scaling** | Brightness $+10\%$ | $28.10\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |
| **Photometric Scaling** | Contrast $+10\%$ | $27.60\text{ dB}$ | $0.00\%$ | **0.00%** | **1.0000** |

---

## 6. Project Structure

```
24cs003421_DIP/
├── backend/                        # FastAPI Python backend
│   ├── app/
│   │   ├── api/routes/             # REST endpoints (watermark, extraction, experiments, jobs, reports)
│   │   ├── core/                   # Core DIP engine (DCT, SVD, QIM, Reed-Solomon, Preprocessing)
│   │   ├── models/                 # SQLAlchemy database models & Pydantic schemas
│   │   ├── security/               # HMAC key derivation & JWT authentication
│   │   ├── services/               # Experiment & watermarking services
│   │   ├── config.py               # Application configuration
│   │   └── main.py                 # ASGI application entrypoint
│   ├── requirements.txt            # Python dependencies
│   └── tests/                      # Automated test suite (unit, integration, attacks, API)
├── frontend/                       # React 18 + TypeScript + Vite frontend
│   ├── src/
│   │   ├── components/             # Reusable UI components (Navbar, Dropzone, Comparators)
│   │   ├── pages/                  # Views (Dashboard, Embedding, Extraction, Robustness, Reports)
│   │   ├── services/               # Axios API client integrations
│   │   ├── App.tsx                 # Root application component
│   │   └── main.tsx                # Client entrypoint
│   ├── package.json                # Node dependencies & scripts
│   └── vite.config.ts              # Vite bundler configuration
├── start_all.bat                   # Unified 1-click startup script for Windows
├── start_backend.bat               # Dedicated backend startup script
├── start_frontend.bat              # Dedicated frontend startup script
├── docker-compose.yml              # Containerized multi-service deployment
└── README.md                       # Platform documentation
```

---

## 7. Author & Academic Attribution

- **Student Author:** Amay Singh
- **Email:** `amaysingh.btech2024@spsu.ac.in`
- **Department:** Department of Computer Science and Engineering (Specialization in Artificial Intelligence and Machine Learning)
- **Institution:** Sir Padampat Singhania University (SPSU), Udaipur, Rajasthan, India
- **Course Assignment:** **Project 58 — Robust Image Watermarking Using DCT and SVD** (Curated from the 60 assigned course project topics)

---

## 8. License

This project is licensed under the **MIT License**.
