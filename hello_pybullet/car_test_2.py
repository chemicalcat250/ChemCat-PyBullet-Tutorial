import pybullet as p
import pybullet_data
import time

# 1. 初始化仿真环境
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

# 2. 加载地面和机器人
planeId = p.loadURDF("plane.urdf")
# 确保 robot.urdf 与此脚本在同一目录下
robotId = p.loadURDF("robot.urdf", [0, 0, 0.15], useFixedBase=False)

# 3. 添加控制滑块 (Debug Parameters)
# 控制轮子速度
wheel_velocity = p.addUserDebugParameter("Wheel Velocity", -20, 20, 0)
# 控制手臂伸缩 (Prismatic)
arm_pos = p.addUserDebugParameter("Arm Extension", 0, 0.3, 0)
# 控制夹爪旋转 (Revolute)
gripper_pos = p.addUserDebugParameter("Gripper Rotation", -1.57, 1.57, 0)

# 获取关节索引映射（可选，方便调试）
num_joints = p.getNumJoints(robotId)
print(f"Robot has {num_joints} joints.")

# 4. 仿真循环
while True:
    # 读取滑块数值
    v = p.readUserDebugParameter(wheel_velocity)
    a = p.readUserDebugParameter(arm_pos)
    g = p.readUserDebugParameter(gripper_pos)

    # 控制 4 个轮子 (关节索引 0, 1, 2, 3)
    for i in range(4):
        p.setJointMotorControl2(robotId, i, p.VELOCITY_CONTROL, targetVelocity=v)

    # 控制伸缩臂 (关节索引 4)
    p.setJointMotorControl2(robotId, 4, p.POSITION_CONTROL, targetPosition=a)

    # 控制夹爪 (关节索引 5)
    p.setJointMotorControl2(robotId, 5, p.POSITION_CONTROL, targetPosition=g)

    p.stepSimulation()
    time.sleep(1. / 240.)

p.disconnect()