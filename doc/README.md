# ImageBatchProcessor

**Author:** Tobiáš Gruber	  
**School:** SPŠE Ječná  
**Project Type:** Parallel Programming

---

## 1. Project Description
This application is a **high-performance multi-threaded image processor**. It demonstrates the solution to the **Producer-Consumer problem** in a real-world scenario.

The application monitors a source directory for images, distributes the workload across multiple worker threads (Consumers), and processes them (resizing) in parallel. This ensures maximum CPU utilization and significantly faster processing compared to a sequential approach.

### Key Features
- **Parallel Processing:** Uses `threading` to process multiple images simultaneously.
- **Producer-Consumer Pattern:** Implements a thread-safe `queue.Queue` for task distribution.
- **Configurability:** All parameters are strictly separated in a JSON configuration file.
- **Robust Logging:** Detailed logging to both file and console.

---

## 2. Architecture & Design

### Architecture Overview
The application follows the **Single Responsibility Principle (SRP)**.
- **AppManager:** The controller that orchestrates the application lifecycle.
- **ConfigLoader:** Handles JSON parsing and validation.
- **ImageWorker:** A dedicated thread class for image manipulation.
- **Queue:** The synchronization primitive acting as a buffer between Producer (Main) and Consumers (Workers).

### Workflow (Activity Diagram Description)
1. **Start:** Application loads `config.json`.
2. **Init:** `AppManager` initializes the Queue and spawns `N` Worker threads.
3. **Produce:** Main thread scans the input folder and pushes filenames to the Queue.
4. **Consume:** Worker threads pick files from Queue -> Resize -> Save to output.
5. **Sync:** Main thread waits (`join`) until Queue is empty.
6. **Stop:** Workers are signaled to stop via `Event`.

---

## 3. Installation & Requirements

### Prerequisites
- Python 3.8 or higher
- Pip (Python Package Installer)

- pip install -r requirements.txt

### Installation
1. 
   ```bash
   git clone <https://github.com/tobiasgruber730/ImageBatchProcessor.git>