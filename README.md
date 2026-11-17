# ROS2_Hardware_Software

A 3-node ROS 2 system bridging an STM32 microcontroller with a ROS 2
environment via **micro-ROS**. An HC-SR04 ultrasonic sensor measures
distance; a control node maps distance to motor speed; an actuator node
drives DC motor through an L298N and triggers a buzzer at a safety
threshold.

**Goal:** prove a working hardware/software bridge, document it
professionally, and build the foundation for a Nav2 (navigation) course.

---

## 🎯 Project Overview

| Layer | Component | Runs On | Language |
|---|---|---|---|
| Sensor + Actuator firmware | HC-SR04, L298N, buzzer | STM32 | C (micro-ROS / rclc) |
| Control logic | linear mapping, thresholds | PC | Python (`rclpy`) |
| Actuator / alarm logic | PWM commands, safety logic | PC + STM32 | Python + C |
| Visualization & recording | rqt_graph, rqt_plot, ros2 bag | PC | CLI |

**Communication:** micro-ROS over serial (DDS-XRCE), bridged by the
micro-ROS Agent running in Docker.

---

## 🗺️ Project Phases

Each phase has its own folder under `docs/` with a detailed write-up
of what was done, what was learned, and what the aim was. Links are
activated as each phase is completed.

| # | Phase | Aim | Status | Notes |
|---|---|---|---|---|
| 1 | **Toolchain & Communication** | Get the micro-ROS Agent running and prove a minimal STM32 node appears in `ros2 topic list`. | ⏳ In progress | [docs/phase_01_toolchain](docs/phase_01_toolchain/README.md) |
| 2 | **Hardware Wiring & Bare-Metal Test** | Wire HC-SR04 (with voltage divider), L298N, and buzzer; verify each with a plain Arduino sketch before ROS. | ⬜ Pending | [docs/phase_02_hardware](docs/phase_02_hardware/README.md) |
| 3 | **micro-ROS Firmware (C)** | Publish `/distance` (Float32), subscribe to `/cmd_speed` (Int32), drive PWM and buzzer safety logic. | ⬜ Pending | [docs/phase_03_firmware](docs/phase_03_firmware/README.md) |
| 4 | **Python ROS 2 Nodes** | Control Node (linear mapping, parameters) and Actuator/Alarm Node logic. | ⬜ Pending | [docs/phase_04_ros2_nodes](docs/phase_04_ros2_nodes/README.md) |
| 5 | **Launch File & Parameters** | One-command launch, YAML parameter file, runtime parameter changes. | ⬜ Pending | [docs/phase_05_launch_params](docs/phase_05_launch_params/README.md) |
| 6 | **Visualization & Bag Recording** | rqt_graph, rqt_plot, ros2 bag record/play. | ⬜ Pending | [docs/phase_06_visualization](docs/phase_06_visualization/README.md) |
| 7 | **Documentation & Portfolio Polish** | Wiring diagram, architecture diagram, demo GIF, final README. | ⬜ Pending | [docs/phase_07_documentation](docs/phase_07_documentation/README.md) |
| 8 | **Integration Debugging** | Resolve serial timing, QoS, agent reconnection issues. | ⬜ Pending | [docs/phase_08_integration](docs/phase_08_integration/README.md) |

**Legend:** ⬜ Pending · ⏳ In progress · ✅ Complete

---

## 🔧 Hardware

- STM32 microcontroller (micro-ROS compatible)
- HC-SR04 ultrasonic sensor
- L298N motor driver +  DC motor
- Active buzzer
- Breadboard, resistors (voltage divider for HC-SR04 ECHO), jumper wires
- External battery pack for motors

---

## 📚 Learning Outcomes

- **Hardware/Software Bridge:** micro-ROS on STM32, serial transport,
  Docker-based Agent.
- **ROS 2 Core:** publisher/subscriber, custom launch files, parameters.
- **Control Logic:** linear mapping and threshold-based safety .
- **Hardware Actuation:** PWM to L298N, digital output to buzzer.
- **Professional Workflow:** version control, per-phase documentation,
  data visualization, bag record/replay.

---
# Phase 1: launch the micro-ROS Agent (after firmware is flashed)
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:jazzy serial --dev /dev/ttyACM0 -v6
