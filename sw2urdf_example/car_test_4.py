import pybullet as p
import os
import time
import pybullet_data

# 1. 初始化仿真环境
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

# 加载地面
p.loadURDF("plane.urdf")

# 2. 定位并加载你的 URDF 模型
# 请确保此脚本与 model 文件夹在同一目录下
urdf_path = os.path.join(os.getcwd(), "car.SLDASM/urdf/car.SLDASM.urdf")

# 加载机器人，并稍微抬高初始位置防止掉入地面
robot_id = p.loadURDF(urdf_path, [0, 0, 0.1], useFixedBase=False)

# 3. 创建控制滑块 (Debug Parameters)
# 参数名称, 最小值, 最大值, 初始值
# 控制前进/后退的速度 (-15 到 15)
vel_slider = p.addUserDebugParameter("Car Velocity", -15, 15, 0)

# 控制伸缩杆位置 (参考 URDF limit: -0.03 到 0.00)
arm_slider = p.addUserDebugParameter("Arm Extension", -0.03, 0.00, 0)

# 控制爪子开合 (参考 URDF limit: -1.2 到 1.2)
gripper_slider = p.addUserDebugParameter("Gripper Rotation", -1.2, 1.2, 0)

# 关节索引映射
wheel_indices = [0, 1, 2, 3] # 四个轮子
arm_index = 4                # 伸缩臂
gripper_index = 5            # 夹爪

# 4. 实时仿真循环
while True:
    # A. 读取滑块当前的数值
    target_velocity = p.readUserDebugParameter(vel_slider)
    target_arm_pos = p.readUserDebugParameter(arm_slider)
    target_gripper_pos = p.readUserDebugParameter(gripper_slider)

    for i in wheel_indices:
        p.setJointMotorControl2(bodyUniqueId=robot_id,
                                jointIndex=i,
                                controlMode=p.VELOCITY_CONTROL,
                                targetVelocity=target_velocity,
                                force=10) # 适当给一点力矩

    # C. 控制伸缩杆 (使用位置控制 POSITION_CONTROL)
    p.setJointMotorControl2(bodyUniqueId=robot_id,
                            jointIndex=arm_index,
                            controlMode=p.POSITION_CONTROL,
                            targetPosition=target_arm_pos,
                            force=30) # 伸缩需要较大推力

    # D. 控制爪子 (使用位置控制 POSITION_CONTROL)
    p.setJointMotorControl2(bodyUniqueId=robot_id,
                            jointIndex=gripper_index,
                            controlMode=p.POSITION_CONTROL,
                            targetPosition=target_gripper_pos,
                            force=20) #

    p.stepSimulation()
    time.sleep(1./240.) # 维持仿真步长