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

## 🧠 System Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                          Personal PC (Ubuntu)                        │
│                                                                      │
│   ┌────────────────────┐        ┌──────────────────────────────┐     │
│   │  micro-ROS Agent   │        │       Control Node           │     │
│   │     (Docker)       │        │         (Python)             │     │
│   │                    │        │                              │     │
│   │  serial bridge     │        │  sub: /distance  (Float32)   │     │
│   │  /dev/serial/by-id │        │  pub: /cmd_speed (Int32)     │     │
│   │        │           │        │  linear mapping + deadband   │     │
│   └────────┼───────────┘        └──────────────┬───────────────┘     │
│            │                                   │                     │
│            │        ROS 2 DDS Network          │                     │
│            │   ┌───────────────────────────────┘                     │
│            │   │                                                     │
│            │   │   ┌──────────────────────────────┐                  │
│            │   │   │    Actuator / Alarm Node     │                  │
│            │   │   │          (Python)            │                  │
│            │   │   │                              │                  │
│            │   │   │  sub: /cmd_speed (Int32)     │                  │
│            │   │   │  sub: /distance  (Float32)   │                  │
│            │   │   │  monitor + safety logging    │                  │
│            │   │   └──────────────────────────────┘                  │
│            │   │                                                     │
│            │   │   ┌──────────────────────────────┐                  │
│            │   │   │   Visualization & Analysis   │                  │
│            │   │   │  rqt_graph · rqt_plot        │                  │
│            │   │   │  ros2 bag record / play      │                  │
│            │   │   └──────────────────────────────┘                  │
│            │   │                                                     │
└────────────┼───┼─────────────────────────────────────────────────────┘
             │   │
             │   │  USB Serial — DDS-XRCE (micro-ROS transport)
             │   │
┌────────────┼───┼─────────────────────────────────────────────────────┐
│            │   │                  ESP32 (hardware)                    │
│            ▼   ▼                                                     │
│   ┌──────────────────────────────────────────────┐                   │
│   │        micro-ROS Firmware (C++ / Arduino)    │                   │
│   │                                              │                   │
│   │   pub: /distance  (Float32, cm)              │                   │
│   │   sub: /cmd_speed (Int32, 0–255)             │                   │
│   │   local safety: buzzer < threshold           │                   │
│   └───────┬─────────────────────┬────────────────┘                   │
│           │                     │                                    │
│   ┌───────▼───────┐     ┌───────▼────────┐     ┌──────────────────┐  │
│   │   HC-SR04     │     │     L298N      │     │     Buzzer       │  │
│   │  Ultrasonic   │     │  Motor Driver  │     │  Safety Alarm    │  │
│   │               │     │                │     │                  │  │
│   │  TRIG / ECHO  │     │ ENA IN1 IN2    │     │  digital GPIO    │  │
│   │  (voltage     │     │ ENB IN3 IN4    │     │                  │  │
│   │   divider)    │     │                │     │                  │  │
│   └───────────────┘     └───┬────────┬───┘     └──────────────────┘  │
│                             │        │                               │
│                        ┌────▼──┐  ┌──▼────┐                          │
│                        │Motor A│  │Motor B│                          │
│                        └───────┘  └───────┘                          │
│                                                                      │
│   Power: external battery pack → L298N 12V → common GND with ESP32   │
└──────────────────────────────────────────────────────────────────────┘
```

**Data flow:**

1. **ESP32 → PC:** HC-SR04 distance is read and published as `/distance` (`Float32`, cm) through the micro-ROS Agent.
2. **Control Node:** subscribes to `/distance`, applies linear mapping (far = fast, close = slow, `< safety_distance` = stop), publishes `/cmd_speed` (`Int32`, 0–255).
3. **ESP32 ← PC:** subscribes to `/cmd_speed` and writes PWM to the L298N `ENA`/`ENB` pins.
4. **Local safety:** the ESP32 independently fires the buzzer below the hard threshold — a fallback that works even if the PC-side node stalls.
5. **Observability:** `rqt_graph`, `rqt_plot`, and `ros2 bag` sit on the DDS network for live visualization and later replay.

   
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
