<div align="center">

# 🔍 Gas Leak Detection via CO2-Guided Crack Inspection

### 🤖 Autonomous TurtleBot3 Navigation with YOLO-World XL and Depth-Anything-V2

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ROS 2 Humble](https://img.shields.io/badge/ROS%202-Humble-green.svg)](https://docs.ros.org/en/humble/)
[![Ultralytics](https://img.shields.io/badge/ultralytics-8.3-purple.svg)](https://github.com/ultralytics/ultralytics)
[![Dataset](https://img.shields.io/badge/dataset-Roboflow-orange.svg)](https://universe.roboflow.com/gazxard/pipe-crack-detection/dataset/1)

</div>

---

**TL;DR** &mdash; A ROS 2 system that detects gas leaks on pipe infrastructure by fusing CO2 concentration sensing with visual crack detection. A TurtleBot3 equipped with a SenseAir S8 sensor monitors CO2 levels while a fine-tuned YOLO-World XL model (mAP@50-95: **86.9%**, Precision: **98.0%**, Recall: **97.5%**) and Depth-Anything-V2 monocular depth estimation identify and approach cracked pipe segments.

## ❓ Why This Matters

Manual pipe inspection in industrial and urban environments is slow, hazardous, and error-prone. Gas leaks on pipe networks often manifest as both elevated CO2 concentrations and visible surface cracks &mdash; but neither signal alone is sufficient for reliable detection. This system combines both modalities in a closed-loop autonomous pipeline: CO2 readings flag anomalous regions, and visual crack detection confirms the source at close range.

## 📊 Key Results

<table>
<tr>
<td>

### 🎯 Crack Detection (YOLO-World XL)

| Metric | Test Set | Val Set |
|--------|:--------:|:-------:|
| mAP@50-95 | **0.869** | 0.858 |
| mAP@50 | 0.984 | 0.977 |
| Precision | 0.980 | 0.988 |
| Recall | 0.975 | 0.963 |
| F1 | 0.978 | 0.976 |

<sub>Fine-tuned on 2,617 images (3 crack classes). Trained on NVIDIA DGX A100.</sub>

</td>
<td>

### 🏷️ Per-Class AP@50-95

| Class | AP@50-95 | AP@50 |
|-------|:--------:|:-----:|
| Dummy crack | **95.6%** | 99.5% |
| PVC pipe crack | 91.2% | 99.2% |
| Paper crack | 74.0% | 97.2% |

<sub>400 labels per class. Substrate complexity governs detection difficulty.</sub>

</td>
</tr>
</table>

### ⏱️ Inference Latency (CPU, TurtleBot3 Laptop)

| Component | Mean &pm; Std |
|-----------|:---:|
| YOLO-World XL | 860.65 &pm; 52.05 ms |
| Depth-Anything-V2 | 1019.65 &pm; 66.23 ms |
| Total pipeline | 1880.31 &pm; 101.36 ms |
| Throughput | **0.53 &pm; 0.03 FPS** |

<sub>92 frames, CPU-only inference. GPU deployment recommended for real-time operation.</sub>

## 🏗️ System Architecture

The system is organized into three functional areas:

| Module | Description | Hardware |
|--------|-------------|----------|
| 📡 **Network Latency** | ROS 2 pub/sub timing analysis between TurtleBot3 and laptop | TurtleBot3 Waffle Pi |
| 🌫️ **CO2 Sensing** | SenseAir S8 sensor driver over UART/Modbus | Raspberry Pi + SenseAir S8 |
| 👁️ **Detection + Navigation** | YOLO-World XL crack detection, Depth-Anything-V2 depth estimation, reactive navigation, web GUI | Laptop (CUDA optional) |

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
# 1. Clone the repository
git clone git@github.com:gazzard-ust/gas-leak-detection.git
cd gas-leak-detection

# 2. Install Python dependencies
pip install torch torchvision ultralytics transformers fastapi uvicorn opencv-python pillow numpy pyserial

# 3. Build the ROS 2 package
colcon build --packages-select MEx3
source install/setup.bash

# 4. Download model weights (not included in repo)
# Place best.pt in src/MEx3/MEx3/
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
ros2 run senseair_s8_driver senseair_s8_node
```

**Terminal 3** &mdash; 📹 Camera Publisher (on robot):
```bash
export ROS_DOMAIN_ID=27
python3 nodes/image_publisher.py
```

**Terminal 4** &mdash; 🖥️ Detection GUI (laptop):
```bash
export ROS_DOMAIN_ID=27
source install/setup.bash
ros2 run MEx3 gazzard_gui_detection_final
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

## ⚙️ Training Configuration

| Parameter | Value |
|-----------|-------|
| Model | YOLO-World XL (fine-tuned) |
| Optimizer | AdamW |
| Learning rate | 2e-4 (cosine decay to 1%) |
| Epochs | 100 (early stopping, patience=20) |
| Image size | 640 |
| Augmentation | HSV, flip, mosaic, mixup, rotation, scale, shear |
| Weight decay | 0.05 |
| Hardware | NVIDIA DGX A100 |

## 📁 Repository Structure

```
.
├── 🧠 src/MEx3/                               # ROS 2 detection package (colcon workspace)
│   ├── MEx3/
│   │   ├── __init__.py
│   │   ├── gazzard_gui_detection_final.py   # Production: crack detection + navigation
│   │   ├── gazzard_gui.py                   # Base reactive navigation GUI
│   │   ├── gazzard_gui_v2.py               # Crack detection with geometric filtering
│   │   ├── gazzard_gui_v3.py               # Detection variant v3
│   │   ├── image_publisher.py              # Camera capture node
│   │   ├── image_subscriber.py             # Core detection + depth + navigation
│   │   └── background.png                  # Web UI background
│   ├── setup.py                             # ROS 2 ament_python package config
│   ├── package.xml                          # Package manifest
│   ├── resource/MEx3
│   └── test/                                # Standard ament tests
├── 📡 nodes/                                   # Standalone ROS 2 nodes
│   ├── turtlebot_publisher.py               # Publishes Twist + timing to /cmd_vel
│   ├── laptop_subscriber.py                 # Subscribes & logs latency stats
│   └── senseair_s8_publisher.py             # SenseAir S8 CO2 sensor (Modbus/UART)
├── 🔧 scripts/                                 # Setup & installation
│   ├── install_complete_system.sh           # Full system installer
│   └── setup_raspberry_pi_helper.sh         # Raspberry Pi UART setup
├── 🧪 tests/                                   # Sensor validation
│   └── test_senseair_s8.py                  # Standalone SenseAir S8 test
├── 📚 docs/                                    # Documentation
│   ├── detection_navigation.md              # Detailed detection & navigation docs
│   ├── YOLOWORLD_FINETUNING_EXPLAINED.md    # Training methodology
│   ├── EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md # Evaluation protocol
│   └── flow_chart                           # System flow diagram
├── TERMINAL_COMMANDS                        # Quick-start terminal commands
├── .gitignore
└── 📋 README.md                                # This file
```

## 📚 Documentation

- [`docs/detection_navigation.md`](docs/detection_navigation.md) &mdash; Detailed documentation for the detection and navigation subsystem
- [`docs/YOLOWORLD_FINETUNING_EXPLAINED.md`](docs/YOLOWORLD_FINETUNING_EXPLAINED.md) &mdash; YOLOWorld fine-tuning process
- [`docs/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md`](docs/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md) &mdash; Validation and measurement procedures

## 📝 Citation

```bibtex
@thesis{pangaliman2026gasleak,
  title={Gas Leak Detection and Localization via CO2-Guided Crack Inspection
         on Pipe Infrastructure Using Autonomous Mobile Robot},
  author={Pangaliman, Ma. Madecheen S. and Biasbas, Mark Kenneth and
          Flores, Faustino Miguel and Gatchalian, Carl Christian and
          Velasco, Lorin Angela and Yadao, Dulce Maria},
  school={University of the Philippines},
  year={2026}
}
```

## 📄 License

Code: MIT &middot; Dataset: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
