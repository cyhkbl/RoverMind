# ROS 2 机器人具身智能演示

> 基于 ROS 2 Humble + Gazebo Ignition，通过 JSON 动作序列 / 自然语言指令驱动机器人运动控制与语音播报，支持闭环导航与障碍物规避。

```
                         ┌──────────────────────┐
                         │   自然语言指令         │
                         │  "前进2米然后左转"     │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  IntentParserNode     │  walk_talk_run_llm
                         │  Claude API → JSON    │
                         └──────────┬───────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────┐
│  config/sequence.json                                         │
│  ┌──────────────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  motion_distance  │→│  speech   │→│  motion_angle     │→… │
│  │  前进2m @0.3m/s   │  │ "到达1"  │  │  左转90° @0.5°/s │    │
│  └──────────────────┘  └──────────┘  └──────────────────┘    │
└────────────────────────┬──────────────────────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  SequenceRunnerNode │  walk_talk_run_core
              │  ─────────────────  │
              │  · 闭环里程计控制    │  ← /odom feedback
              │  · 障碍物规避暂停    │  ← /scan → ObstacleAvoider
              │  · 速度安全校验      │
              │  · 优雅中断停止      │
              └──────┬──────┬──────┘
                     │      │
            cmd_vel  │      │ speech_cue
          (Twist)    │      │ (String)
                     ▼      ▼
              ┌───────────────────┐
              │  Gazebo 仿真      │  walk_talk_run_sim
              │  /odom + /scan    │
              │  差速底盘 + LiDAR  │
              └───────────────────┘
```

## 五种动作类型

| 类型 | 控制方式 | 关键参数 | 说明 |
|------|----------|----------|------|
| `motion_distance` | **闭环** (odom) | `distance`, `speed` | 基于里程计反馈移动指定距离 (米) |
| `motion_angle` | **闭环** (odom) | `angle`, `speed` | 基于里程计反馈旋转指定角度 (弧度) |
| `motion` | 开环 (时间) | `linear_x/y`, `angular_z`, `duration` | 按固定速度运行指定时长 (兼容旧版) |
| `speech` | — | `text`, `pause_after_sec` | 语音/日志播报 |
| `pause` | — | `duration` | 静默等待 |

闭环控制使用 P 控制器 (Proportional)，通过 `/odom` 话题实时反馈机器人位置与航向。速度指令经 `max_linear_speed` / `max_angular_speed` 硬限幅。

## 快速开始

### Docker（推荐）

```bash
# 构建
docker compose build

# 运行 Gazebo 仿真 + 闭环序列
docker compose run --rm sim

# 运行 LLM 自然语言控制（需设置 API Key）
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up llm
# 另一终端发送指令
docker compose run --rm test-command
```

### 本地安装

```bash
# 依赖
sudo apt install ros-humble-ros-gz-sim ros-humble-ros-gz-bridge \
  ros-humble-robot-state-publisher ros-humble-xacro
pip install anthropic

# 构建
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

# 仿真模式
ros2 launch walk_talk_run_sim sim.launch.py

# 纯序列运行（无 Gazebo）
ros2 launch walk_talk_run_core sequence_runner.launch.py
```

## 自定义动作序列

```json
[
  {"type": "motion_distance", "distance": 2.0, "speed": 0.3},
  {"type": "speech", "text": "到达检查点一", "pause_after_sec": 1.0},
  {"type": "motion_angle", "angle": -1.57, "speed": 0.5},
  {"type": "motion_distance", "distance": 1.5, "speed": 0.3},
  {"type": "speech", "text": "到达检查点二", "pause_after_sec": 1.0},
  {"type": "pause", "duration": 0.5}
]
```

## 仓库结构

```
ROS_WALK_TALK_RUN/
├── docker/
│   ├── Dockerfile                    # ROS 2 Humble + Gazebo 环境
│   └── entrypoint.sh
├── docker-compose.yml                # 一键启动
├── pyproject.toml                    # ruff + mypy 配置
├── .pre-commit-config.yaml
└── src/
    ├── walk_talk_run_core/           # 核心包：序列控制 + 闭环 + 避障
    │   ├── walk_talk_run_core/
    │   │   ├── sequence_model.py     # 序列解析 + 校验 (5种类型)
    │   │   ├── sequence_runner.py    # ROS 2 节点：执行序列
    │   │   ├── closed_loop.py        # 闭环控制器 (P控制)
    │   │   └── obstacle_avoider.py   # 障碍物检测节点
    │   ├── config/default_sequence.json
    │   ├── launch/
    │   └── test/
    │
    ├── walk_talk_run_sim/            # 仿真包：Gazebo + URDF
    │   ├── urdf/diff_drive.urdf.xacro  # 差速底盘 URDF
    │   ├── world/indoor.sdf            # 室内仿真世界
    │   ├── config/default_sequence_sim.json
    │   └── launch/sim.launch.py        # 一键启动仿真
    │
    └── walk_talk_run_llm/            # LLM 包：自然语言 → 动作序列
        ├── walk_talk_run_llm/
        │   └── intent_parser.py      # Claude API 意图解析
        ├── launch/intent_parser.launch.py
        └── test/
```

## 可配置参数

### SequenceRunnerNode

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `cmd_vel_topic` | `/cmd_vel` | 速度指令 topic |
| `speech_topic` | `""` | 语音 topic（空=仅日志） |
| `sequence_file` | 包内默认 | JSON 序列文件路径 |
| `publish_hz` | `20.0` | 速度发布频率 (Hz) |
| `max_linear_speed` | `1.0` | 线速度上限 (m/s) |
| `max_angular_speed` | `1.0` | 角速度上限 (rad/s) |
| `obstacle_topic` | `/obstacle_detected` | 障碍物状态 topic |

### ObstacleAvoiderNode

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `scan_topic` | `/scan` | 激光雷达 topic |
| `obstacle_distance` | `0.5` | 障碍物触发距离 (m) |

### IntentParserNode

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input_topic` | `/nl_command` | 自然语言输入 topic |
| `output_topic` | `/parsed_sequence` | 解析结果输出 topic |
| `model` | `claude-sonnet-4-20250514` | Claude 模型版本 |

## 测试

```bash
colcon test --packages-select walk_talk_run_core walk_talk_run_llm
colcon test-result --verbose
```

## 设计决策

- **闭环 > 开环**：`motion_distance` / `motion_angle` 基于 `/odom` 反馈控制，比纯时间控制更精确、更安全
- **JSON 驱动**：运动逻辑与代码解耦，无需重编译即可调整行为
- **模块化多包**：core / sim / llm 解耦，可独立使用
- **Docker 化**：一键复现，跨平台一致体验
- **速度硬限幅 + 避障**：双重安全机制，防止配置错误或环境变化导致碰撞
- **优雅停止**：SIGINT/SIGTERM 后立即零速停止

## Roadmap

- [x] 闭环里程计控制 (motion_distance / motion_angle)
- [x] 障碍物规避 (LiDAR scan → 自动暂停)
- [x] Gazebo Ignition 仿真 (差速底盘 + LiDAR)
- [x] LLM 自然语言意图解析 (Claude API)
- [x] Docker 容器化部署
- [x] CI 测试流水线 (GitHub Actions)
- [ ] Nav2 导航栈集成 (NavigateToPose Action)
- [ ] 行为树重构 (py_trees_ros)
- [ ] Lifecycle Node (工业级节点管理)
- [ ] 真机适配 (智源灵犀X2)

## 安全提醒

接入真机前请确认：场地安全、急停可用、限速合理、周围无障碍物。

## 许可证

Apache-2.0
