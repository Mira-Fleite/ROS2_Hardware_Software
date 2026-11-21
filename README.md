# ROS 2 Hardware-in-the-Loop Collision Avoidance System

A 3-node ROS 2 system bridging an **ESP32** microcontroller with a ROS 2
environment via **micro-ROS**. An HC-SR04 ultrasonic sensor measures
distance; a control node maps distance to motor speed; an actuator node
drives two DC motors through an L298N and triggers a buzzer at a safety
threshold.

The goal is to demonstrate a working hardware/software bridge, document
it professionally.

---

## 🎯 Project Overview

| Layer | Component | Runs On | Language |
|---|---|---|---|
| Sensor + Actuator firmware | HC-SR04, L298N, buzzer | ESP32 | C++ (Arduino + `micro_ros_arduino`) |
| Control logic | linear mapping, thresholds | PC | Python (`rclpy`) |
| Actuator / alarm logic | PWM commands, safety logic | PC + ESP32 | Python + C++ |
| Visualization & recording | rqt_graph, rqt_plot, ros2 bag | PC | CLI |

**Communication:** micro-ROS over serial (DDS-XRCE), bridged by the
micro-ROS Agent running in Docker.

**Hardware/Toolchain note:** The entire workflow — firmware build, micro-ROS
Agent, and ROS 2 stack — runs on a single Ubuntu machine. No external IDE
or second workstation is required.

---

## 🗺️ Project Phases

Each phase has its own folder under `docs/` with a detailed write-up
of what was done, what was learned, and what the aim was. Links are
activated as each phase is completed.

| # | Phase | Aim | Status | Notes |
|---|---|---|---|---|
| 0 | **ESP32 Primer** | LED → UART → PWM → sensor → motor → buzzer, ROS-free. | ⏳ In progress | [docs/phase_00_primer](docs/phase_00_primer/README.md) |
| 1 | **Toolchain & Handshake** | Minimal micro-ROS node visible in `ros2 topic echo`. | ⬜ Pending | [docs/phase_01_toolchain](docs/phase_01_toolchain/README.md) |
| 2 | **Hardware Assembly** | Dual motor, voltage divider verified, calibration table. | ⬜ Pending | [docs/phase_02_hardware](docs/phase_02_hardware/README.md) |
| 3 | **micro-ROS Firmware** | `/distance` pub, `/cmd_speed` sub, PWM, buzzer. | ⬜ Pending | [docs/phase_03_firmware](docs/phase_03_firmware/README.md) |
| 4 | **Python ROS 2 Nodes** | Control + Actuator nodes. | ⬜ Pending | [docs/phase_04_ros2_nodes](docs/phase_04_ros2_nodes/README.md) |
| 5 | **Launch & Params** | One command, YAML thresholds, runtime tuning. | ⬜ Pending | [docs/phase_05_launch_params](docs/phase_05_launch_params/README.md) |
| 6 | **Visualization & Bag** | rqt_graph, rqt_plot, record/playback. | ⬜ Pending | [docs/phase_06_visualization](docs/phase_06_visualization/README.md) |
| 7 | **Portfolio Polish** | Architecture diagram, demo GIF, final README. | ⬜ Pending | [docs/phase_07_documentation](docs/phase_07_documentation/README.md) |
| 8 | **Integration Debugging** | QoS, serial timing, reconnection log. | ⬜ Pending | [docs/phase_08_integration](docs/phase_08_integration/README.md) |

**Legend:** ⬜ Pending · ⏳ In progress · ✅ Complete

---

## 🔧 Hardware

- ESP32 development board 
- HC-SR04 ultrasonic sensor
- L298N motor driver + 2 DC motors
- Active buzzer
- Breadboard, resistors (1 kΩ + 2 kΩ voltage divider for HC-SR04 ECHO),
  jumper wires
- External battery pack for motors

---

## 🧠 Architecture
┌─────────────────────────────────────────────────────────────────┐
│ Personal PC (Ubuntu) │
│ │
│ ┌──────────────────┐ ┌──────────────────┐ │
│ │ micro-ROS Agent │ │ Control Node │ │
│ │ (Docker) │ │ (Python) │ │
│ │ │ │ │ │
│ │ /dev/ttyUSB0 ───┼──┐ │ sub: /distance │ │
│ │ │ │ │ pub: /cmd_speed │ │
│ └──────────────────┘ │ └──────────────────┘ │
│ │ ▲ │
│ │ │ /distance │
│ │ │ /cmd_speed │
│ │ ┌────────┴─────────┐ │
│ │ │ Actuator / Alarm │ │
│ │ │ Node │ │
│ │ │ (Python) │ │
│ │ └──────────────────┘ │
│ │ │
│ │ DDS / ROS 2 network │
│ │ │
│ │ ┌──────────────────┐ │
│ │ │ rqt_graph │ │
│ │ │ rqt_plot │ │
│ │ │ ros2 bag │ │
│ │ └──────────────────┘ │
└────────────────────────┼─────────────────────────────────────────┘
│ USB Serial (DDS-XRCE)
┌────────────────────────┼─────────────────────────────────────────┐
│ ESP32 (hardware) │
│ │
│ ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│ │ HC-SR04 │ │ L298N │ │ Buzzer │ │
│ │ Ultrasonic │ │ Motor Driver│ │ (safety alarm) │ │
│ └──────┬──────┘ └──────┬───────┘ └──────────────────┘ │
│ │ │ │
│ ┌──────┴─────────────────┴─────┐ │
│ │ micro-ROS firmware (C++) │ │
│ │ pub /distance (Float32) │ │
│ │ sub /cmd_speed (Int32) │ │
│ │ PWM + digital GPIO │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘


**Data flow:**
1. ESP32 reads HC-SR04 → publishes `/distance` (Float32, cm) to the Agent.
2. Control Node maps distance → speed → publishes `/cmd_speed` (Int32).
3. ESP32 subscribes to `/cmd_speed` → PWM on L298N.
4. ESP32's local safety logic (buzzer) fires independently below threshold.

---

## 📚 Learning Outcomes

- **Hardware/Software Bridge:** micro-ROS on ESP32, serial transport,
  Docker-based Agent.
- **ROS 2 Core:** publisher/subscriber, custom launch files, parameters.
- **Control Logic:** linear mapping and threshold-based safety.
- **Hardware Actuation:** PWM to L298N, digital output to buzzer.
- **Professional Workflow:** version control, per-phase documentation,
  data visualization, bag record/replay.

---
