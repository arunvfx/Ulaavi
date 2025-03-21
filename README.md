# Ulaavi - Stock Footage Loader for Nuke

Ulaavi is a tool designed to help you load, preview, and import stock footage directly inside Nuke. It simplifies the process of working with stock footage by providing an intuitive interface and high-quality previews.

---

## Features
- Load and preview stock footage directly in Nuke.
- High-quality `.mov` previews (replaced GIF previews in version 2.0.0 for better quality).
- Seamless integration with Nuke's workflow.

---

## Installation

### Prerequisites
- **FFmpeg**: Ensure FFmpeg is installed and its directory is added to your system's environment path.
- **Third-Party Packages**:
  - `clique==2.0.0`
  - `opencv-python==4.11.0.86`
  - `numpy==1.26.4`
  - `Pyside2` or `PySide6` (depending on your Nuke version).

### Steps
1. Install the required third-party packages using pip:
   ```bash
   pip install clique==2.0.0 opencv-python==4.11.0.86 numpy==1.26.4 Pyside2
