import pybullet as p
import pybullet_data
import time

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

planeId = p.loadURDF("plane.urdf")
# 加载你刚才创建的 URDF
robotId = p.loadURDF("my_robot.urdf", [0, 0, 0.2])

for i in range(10000):
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()