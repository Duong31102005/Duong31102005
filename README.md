# `Duong31102005` · AI & Robotics

<p align="center">
  <img src="https://img.shields.io/badge/AI%20%2B%20Robotics-0B1220?style=for-the-badge&logo=robotframework&logoColor=00D1FF" alt="AI and Robotics" />
  <img src="https://img.shields.io/badge/Computer%20Vision-111827?style=for-the-badge&logo=opencv&logoColor=5C3EE8" alt="Computer Vision" />
  <img src="https://img.shields.io/badge/ROS%202-111827?style=for-the-badge&logo=ros&logoColor=22314E" alt="ROS 2" />
</p>

> **Building systems that see, listen, and move.**
>
> I work on projects that connect computer vision, speech AI, and embedded robotics—from real-time perception to safe robot control.

## Focus

- Real-time computer vision and object tracking
- Speech recognition and voice interfaces
- Robotics with ROS 2, Raspberry Pi, and ESP32
- Reliable communication and safety mechanisms for hardware

## Featured project

### [AI Robot — Vision & Voice Control](https://github.com/Duong31102005/AI_Robot)

An AI server for a mobile robot, combining YOLO11s person detection and tracking with Vietnamese speech recognition using OpenAI Whisper. The server sends control commands to a Raspberry Pi ROS 2 controller, with an ESP32 handling the motor hardware.

**Stack:** Python · YOLO11s · OpenCV · Whisper · HTTP/JSON · Raspberry Pi · ROS 2 · ESP32

```mermaid
flowchart LR
    Camera --> Vision[YOLO11s detection & tracking]
    Mic[Microphone] --> Speech[Whisper speech recognition]
    Vision --> Server[Python AI server]
    Speech --> Server
    Server -->|HTTP / JSON| Pi[Raspberry Pi · ROS 2]
    Pi --> ESP[ESP32]
    ESP --> Motors[Robot motors]
```

## Tools I use

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/ROS%202-22314E?style=flat-square&logo=ros&logoColor=white" alt="ROS 2" />
  <img src="https://img.shields.io/badge/Raspberry%20Pi-A22846?style=flat-square&logo=raspberrypi&logoColor=white" alt="Raspberry Pi" />
  <img src="https://img.shields.io/badge/ESP32-E7352C?style=flat-square&logo=espressif&logoColor=white" alt="ESP32" />
</p>

## More projects

- [Quản lí khóa học](https://github.com/Duong31102005/Quan-li-khoa-hoc)
- [BTL Nhóm 11](https://github.com/Duong31102005/btl_Nhom11)

---

<p align="center">
  <sub>Learning by building · Vietnam</sub>
</p>

