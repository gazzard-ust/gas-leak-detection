<div align="center">

# 🔍 Gas Leak Detection via CO2-Guided Crack Inspection

### 🤖 Autonomous TurtleBot3 Navigation with YOLO-World XL and Depth-Anything-V2

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ROS 2 Humble](https://img.shields.io/badge/ROS%202-Humble-green.svg)](https://docs.ros.org/en/humble/)
[![Ultralytics](https://img.shields.io/badge/ultralytics-8.3-purple.svg)](https://github.com/ultralytics/ultralytics)
[![Dataset](https://img.shields.io/badge/dataset-Roboflow-orange.svg)](https://universe.roboflow.com/gazxard/pipe-crack-detection/dataset/1)

</div>

---

**TL;DR** &mdash; A ROS 2 system that detects gas leaks on pipe infrastructure by fusing CO2 concentration sensing with visual crack detection. A TurtleBot3 equipped with a SenseAir S8 sensor monitors CO2 levels while a zero-shot YOLO-World XL model (open-vocabulary, no task-specific training; mAP@50-95: **86.9%**, Precision: **98.0%**, Recall: **97.5%**) and Depth-Anything-V2 monocular depth estimation identify and approach cracked pipe segments.

## ❓ Why This Matters

Manual pipe inspection in industrial and urban environments is slow, hazardous, and error-prone. Gas leaks on pipe networks often manifest as both elevated CO2 concentrations and visible surface cracks &mdash; but neither signal alone is sufficient for reliable detection. This system combines both modalities in a closed-loop autonomous pipeline: CO2 readings flag anomalous regions, and visual crack detection confirms the source at close range.

## 📊 Key Results

### 🎯 Crack Detection (YOLO-World XL)

| Metric | Test Set | Val Set |
|--------|:--------:|:-------:|
| mAP@50-95 | **0.869** | 0.858 |
| mAP@50 | 0.984 | 0.977 |
| Precision | 0.980 | 0.988 |
| Recall | 0.975 | 0.963 |
| F1 | 0.978 | 0.976 |

<sub>Zero-shot YOLO-World XL (open-vocabulary text prompts, no task-specific training), evaluated on 2,617 images across 3 crack classes.</sub>

### 🏷️ Per-Class AP@50-95

| Class | AP@50-95 | AP@50 |
|-------|:--------:|:-----:|
| Dummy crack | **95.6%** | 99.5% |
| PVC pipe crack | 91.2% | 99.2% |
| Paper crack | 74.0% | 97.2% |

<sub>400 labels per class. Substrate complexity governs detection difficulty.</sub>

### ⏱️ Inference Latency (CPU, TurtleBot3 Laptop)

| Component | Mean &pm; Std |
|-----------|:---:|
| YOLO-World XL | 892.37 &pm; 60.61 ms |
| Depth-Anything-V2 | 1028.47 &pm; 66.53 ms |
| Total pipeline | 1920.84 &pm; 100.58 ms |
| Throughput | **0.52 &pm; 0.03 FPS** |

<sub>CPU-only inference on the TurtleBot3 laptop. GPU deployment recommended for real-time operation.</sub>

### 🔀 Leak-Source Verification (CO2 + Vision Fusion)

Visual crack detection alone cannot tell a *leaking* crack from a non-leaking one (CO2 is invisible). Fusing CO2 concentration with crack detection over 30 trials (15 leak / 15 no-leak) is what makes leak-source confirmation reliable:

| Method | Accuracy | Precision | Recall | False-Positive Rate |
|--------|:--------:|:---------:|:------:|:-------------------:|
| Detection only | 46.67% | 48.28% | 93.33% | **100%** |
| Detection + CO2 | **90.00%** | **92.86%** | 86.67% | **6.67%** |

<sub>Fusion cuts the false-positive rate from 100% → 6.67% and raises accuracy from 46.67% → 90% (Wilson 95% CI: 74.4–96.5%, n=30).</sub>

## 🏗️ System Architecture

This repository is a ROS 2 workspace containing the `gas_leak_detection` package. See [Quick Start](#-quick-start) for installation.

### 📡 ROS 2 Nodes

| Node | Command | Description |
|------|---------|-------------|
| 📹 Image Publisher | `ros2 run gas_leak_detection image_publisher` | Camera capture &rarr; `/image/compressed` |
| 🖥️ Detection GUI | `ros2 run gas_leak_detection gazzard_gui_detection_final` | Crack detection + depth + navigation + web UI |
| 🤖 TurtleBot Publisher | `ros2 run gas_leak_detection turtlebot_publisher` | Twist commands + timing data |
| 💻 Laptop Subscriber | `ros2 run gas_leak_detection laptop_subscriber` | Latency analysis &amp; logging |
| 🌫️ CO2 Sensor | `ros2 run gas_leak_detection senseair_s8_publisher` | SenseAir S8 Modbus/UART driver |

### 📡 ROS 2 Topics

| Topic | Type | Direction | Description |
|-------|------|-----------|-------------|
| `/image/compressed` | CompressedImage | Pub &rarr; Sub | 📹 Camera frames (640&times;480, 30 FPS) |
| `/cmd_vel` | Twist | Sub &rarr; Robot | 🤖 Movement commands |
| `/co2_concentration` | Float32 | Pub &rarr; Sub | 🌫️ CO2 ppm from SenseAir S8 |
| `/co2_sensor_data` | String (JSON) | Pub &rarr; Sub | 📋 Sensor metadata + response times |
| `/timing_data` | String (JSON) | Pub &rarr; Sub | ⏱️ Network latency measurements |

## 🗂️ Dataset

| | Train | Val | Test | Total |
|---|:---:|:---:|:---:|:---:|
| Images | 2,292 | 217 | 108 | 2,617 |
| Labels per class | 400 | &mdash; | &mdash; | 400 |

Three crack classes on a texture gradient: **Dummy crack** (smooth PVC) &middot; **PVC pipe crack** (smooth PVC, real fractures) &middot; **Paper crack** (porous tissue)

📦 Available on [Roboflow Universe](https://universe.roboflow.com/gazxard/pipe-crack-detection/dataset/1) under CC BY 4.0.

## 🚀 Quick Start

### 📋 Prerequisites

- 🔧 ROS 2 Humble
- 🐍 Python 3.10+
- 💻 CUDA-capable GPU (recommended, not required)
- 🤖 TurtleBot3 Waffle Pi with Raspberry Pi
- 🌫️ SenseAir S8 CO2 sensor (UART)

### 📥 Installation

```bash
# 1. Clone the workspace
git clone git@github.com:gazzard-ust/gas-leak-detection.git
cd gas-leak-detection

# 2. Install Python dependencies
pip install torch torchvision ultralytics transformers fastapi uvicorn opencv-python pillow numpy pyserial

# 3. Build
colcon build --packages-select gas_leak_detection
source install/setup.bash

# 4. Download model weights (not included in repo)
# Place best.pt in src/gas_leak_detection/gas_leak_detection/
```

### ▶️ Running the System

**Terminal 1** &mdash; 🤖 TurtleBot3 Bringup (SSH into robot):
```bash
export TURTLEBOT3_MODEL=waffle_pi
export ROS_DOMAIN_ID=27
ros2 launch turtlebot3_bringup robot.launch.py
```

**Terminal 2** &mdash; 🌫️ CO2 Sensor (SSH into robot):
```bash
export ROS_DOMAIN_ID=27
ros2 run gas_leak_detection senseair_s8_publisher
```

**Terminal 3** &mdash; 📹 Camera Publisher (on robot):
```bash
export ROS_DOMAIN_ID=27
ros2 run gas_leak_detection image_publisher
```

**Terminal 4** &mdash; 🖥️ Detection GUI (laptop):
```bash
export ROS_DOMAIN_ID=27
ros2 run gas_leak_detection gazzard_gui_detection_final
# Open http://localhost:8000 in browser
```

### 🌐 Web Interface Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /set_target?object_name=<name>` | 🎯 Set tracking target |
| `GET /reset` | 🔄 Reset system state |
| `GET /stop` | 🛑 Emergency stop |
| `GET /robot_status` | 📊 Current state JSON |
| `GET /video_feed` | 📹 Live camera stream |
| `GET /depth_feed` | 📐 Live depth visualization |

## ⚙️ Detection Configuration

YOLO-World XL is used **zero-shot**: detection classes are supplied as open-vocabulary text prompts (`dummy crack`, `pvc pipe crack`, `paper crack`) with no task-specific training. Depth-Anything-V2 (ViT) supplies monocular depth for distance estimation.

| Parameter | Value |
|-----------|-------|
| Model | YOLO-World XL (zero-shot, open-vocabulary) |
| Class prompts | dummy crack &middot; pvc pipe crack &middot; paper crack |
| Inference image size | 640 |
| Depth model | Depth-Anything-V2 |
| Inference hardware | CPU (TurtleBot3 laptop) |

## 📁 Repository Structure

```
.                                              # ROS 2 workspace root
├── src/
│   └── gas_leak_detection/                    # ROS 2 ament_python package
│       ├── gas_leak_detection/                # Python module — all nodes
│       │   ├── __init__.py
│       │   ├── gazzard_gui_detection_final.py # 🖥️ Production: crack detection + navigation GUI
│       │   ├── gazzard_gui.py                 # Base reactive navigation GUI
│       │   ├── gazzard_gui_v2.py              # Geometric filtering variant
│       │   ├── gazzard_gui_v3.py              # Detection variant v3
│       │   ├── image_publisher.py             # 📹 Camera capture node
│       │   ├── image_subscriber.py            # Core detection + depth + navigation
│       │   ├── turtlebot_publisher.py         # 🤖 Twist + timing publisher
│       │   ├── laptop_subscriber.py           # 💻 Latency analysis subscriber
│       │   ├── senseair_s8_publisher.py       # 🌫️ CO2 sensor driver (Modbus/UART)
│       │   └── background.png                 # Web UI background
│       ├── resource/gas_leak_detection        # ament resource marker
│       ├── test/                              # Package tests
│       │   ├── test_copyright.py
│       │   ├── test_flake8.py
│       │   ├── test_pep257.py
│       │   └── test_senseair_s8.py            # 🧪 Standalone sensor validation
│       ├── package.xml                        # ROS 2 package manifest
│       ├── setup.py                           # ament_python build config
│       └── setup.cfg                          # Entry point install paths
├── build/                                     # ⚙️ colcon build output (gitignored)
├── install/                                   # ⚙️ colcon install output (gitignored)
├── log/                                       # ⚙️ colcon log output (gitignored)
├── scripts/                                   # 🔧 Setup & installation
│   ├── install_complete_system.sh
│   └── setup_raspberry_pi_helper.sh
├── docs/                                      # 📚 Documentation
│   ├── detection_navigation.md
│   ├── YOLOWORLD_FINETUNING_EXPLAINED.md
│   ├── EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md
│   └── flow_chart
├── TERMINAL_COMMANDS                          # Quick-start guide
├── .gitignore
└── README.md
```

## 📚 Documentation

- [`docs/detection_navigation.md`](docs/detection_navigation.md) &mdash; Detailed detection &amp; navigation subsystem docs
- [`docs/YOLOWORLD_FINETUNING_EXPLAINED.md`](docs/YOLOWORLD_FINETUNING_EXPLAINED.md) &mdash; YOLO-World zero-shot detection setup and class-prompt configuration
- [`docs/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md`](docs/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md) &mdash; Validation and measurement procedures

## 📝 Citation

```bibtex
@inproceedings{biasbas2026gazzard,
  title={Gazzard: Gas Leak Detection using a Mobile Robotic Platform},
  author={Biasbas, Mark Kenneth and Flores, Faustino Miguel and
          Gatchalian, Carl Christian and Velasco, Lorin Angela and
          Yadao, Dulce Maria and Pangaliman, Ma. Madecheen and
          Bautista, Anthony James},
  booktitle={Proc. International Conference on Robotics and Automation Sciences (ICRAS)},
  year={2026}
}
```

## 📄 License

Code: MIT &middot; Dataset: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
