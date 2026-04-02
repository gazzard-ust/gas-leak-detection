# Gas Leak Detection and Localization System

A ROS 2-based robotic system for autonomous gas leak detection and localization using a TurtleBot3 equipped with a CO2 sensor and camera-based crack detection via fine-tuned YOLOWorld.

## System Overview

The system integrates three subsystems to detect, localize, and approach gas leaks on pipes:

| Module | Description |
|--------|-------------|
| **SO1** | ROS 2 network communication — TurtleBot publisher and laptop subscriber for command relay and latency measurement |
| **SO2** | CO2 concentration monitoring — SenseAir S8 sensor driver publishing real-time CO2 readings via ROS 2 |
| **SO3/SO4** | Visual crack detection and reactive navigation — YOLOWorld-based detection with depth estimation and autonomous approach |

## Architecture

```
TurtleBot3 (Raspberry Pi)          Laptop (GPU)
┌──────────────────────┐           ┌──────────────────────────┐
│  Camera              │  ROS 2    │  YOLOWorld Detection     │
│  SenseAir S8 Sensor  │ ───────── │  Depth-Anything V2       │
│  Motor Control       │  Wi-Fi    │  Navigation Controller   │
│                      │           │  Web GUI (FastAPI)       │
└──────────────────────┘           └──────────────────────────┘
```

## Prerequisites

- ROS 2 Humble
- Python 3.8+
- CUDA-capable GPU (for detection model)
- TurtleBot3 Waffle Pi
- SenseAir S8 CO2 sensor

## Installation

```bash
git clone https://github.com/gazzard-ust/gas-leak-detection.git
cd gas-leak-detection
```

### Python Dependencies

```bash
pip install torch torchvision ultralytics transformers fastapi uvicorn opencv-python pillow numpy pyserial
```

### Build the ROS 2 Package (SO3/SO4)

```bash
cd SO34/src
colcon build --packages-select MEx3
source install/setup.bash
```

### Model Weights

The fine-tuned YOLOWorld model (`best.pt`) is not included in this repository due to size constraints. Place your trained model weights in:
- `SO34/src/MEx3/MEx3/best.pt`

## Usage

See `TERMINAL_COMMANDS` for the full step-by-step startup sequence. In summary:

1. **Terminal 1** — TurtleBot bringup
2. **Terminal 2** — CO2 sensor node (`ros2 run senseair_s8_driver senseair_s8_node`)
3. **Terminal 3** — Camera image publisher (`python3 image_publisher.py`)
4. **Terminal 4** — Detection GUI (`ros2 run MEx3 gazzard_gui_detection_final`)

Access the web interface at `http://localhost:8000` to set detection targets and monitor the robot.

## Project Structure

```
gas-leak-detection/
├── SO1/                        # Network communication
│   ├── turtlebot_publisher.py  # TurtleBot command & timing publisher
│   └── laptop_subscriber.py    # Laptop-side latency analyzer
├── SO2/                        # CO2 sensor
│   ├── senseair_s8_publisher.py
│   ├── setup_scripts/
│   └── test_scripts/
├── SO34/                       # Detection & navigation
│   ├── src/MEx3/               # ROS 2 package source
│   ├── EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md
│   ├── YOLOWORLD_FINETUNING_EXPLAINED.md
│   └── README.md               # Detailed SO3/SO4 documentation
├── TERMINAL_COMMANDS           # Startup instructions
└── README.md
```

## Documentation

- [`SO34/README.md`](SO34/README.md) — Detailed documentation for the detection and navigation subsystem
- [`SO34/YOLOWORLD_FINETUNING_EXPLAINED.md`](SO34/YOLOWORLD_FINETUNING_EXPLAINED.md) — YOLOWorld fine-tuning process
- [`SO34/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md`](SO34/EXPECTED_OUTPUTS_MEASUREMENT_GUIDE.md) — Validation and measurement procedures

## License

MIT
