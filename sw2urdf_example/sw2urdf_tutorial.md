# 前言

虽然urdf文件是描述机构内部连杆和关节分布及关系的规范性语言，但是纯手写urdf文件是折磨的，特别是遇上复杂的机器人机构（如四足机器人）。现实中我们一般先进行SW建模，配合插件sw2urdf以及一定的规范自动生成urdf文件。

本文将以一个带伸缩臂和夹爪的四轮小车为例，讲解如何从SW导出urdf并实现小车在pybullet的仿真和控制，

# 一、下载sw2urdf插件

SW本身没有将结构导出为urdf的选项，需要我们下载插件sw2urdf将实现这一过程。

sw2urdf下载地址如下：&#x20;

https://wiki.ros.org/action/fullsearch/sw\_urdf\_exporter?action=fullsearch\&context=180\&value=linkto:%22sw\_urdf\_exporter%22

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NzExZTUzMDg5MDE4NjNmZjFhNmNmN2MxODNhMmM0NDlfTkxkT28xVDhUcFlPb1pkTDFQc0pMTmNBYjZxZ1hEMmNfVG9rZW46VjVRRWJLcEczb0RMM3h4NzFYcGN5M2pGbmpiXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

进入页面后点&#x51FB;**“Download Installer”**&#x7684;蓝色按钮即可下载。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NWYwZmU4NjJhZGE2YTI2Mjg1OTI3YWZiOWQxYWE1MmRfSkZIU3B4bEh1R2tnd2lhN2FndGduYWJxcGJXYUFIbkRfVG9rZW46U1lQd2JBT2hpb0RoTDZ4WlF5OWNtZnVjbnNoXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

下载安装包后随引导安装即可。安装完毕后，在sw界面点开**齿轮图标旁的小倒三角**，点&#x51FB;**“插件”**，

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDU2MDFmNWY0NGQyYTMwZTdlMjJjOTVlNmQzZDhhYzdfVXZxOXpSdkhPQUc0VUM0cFFqU2Jrd3QwNWtJWkx5WmVfVG9rZW46UlZoeWJXQkt3b0hxRmt4dWd2OWNYWmxOblc5XzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

打开插件界面后下滑找到SW2URDF代表安装成功。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MWU1MGM4ZDJkYTAxY2RjNDNlOWQ5NDExMTlhZTk0MWJfSVNMcWNCRHFvd0JTeFM0YUo0d200T29rdFZvNDJGS1RfVG9rZW46U09aMWJBaVFjb2pXd3h4RFZJTWNYenRUbldNXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

# 二、导出模型前的准备工作

为了能顺利导出urdf模型，我们需要按照一定的规范将我们的四轮小车模型组织起来。

2.1.建模小车各个零件

小车底盘base:

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MTJmMWY4YjQwZmQ2YTVkZThkNGRjMDQ5MTBkZDczZGNfNjd2R0QwV3dYeEVRQkFZNFkxdUZnQUhWaXNTekp0eDlfVG9rZW46UzNobmJ0Z1Azb05oZGF4UHNrTWNCVXUybmVoXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

这个底盘比较简单，两侧各引出2个对称的定位柱便于后续装配过程中轮子的定位和配合。

中间则是挖了个槽用来安装伸缩臂，虽然这不是必要的，但是方便后续能直观观察伸缩臂的运动，所以这里也建模出来了。

小车轮子wheel

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MzViOTFkN2UwOTU1YWY1NmM3MWExOWIxZGY5MjJhZGFfN1dKY2RPMUQ1VURoU1J4Z0pNTWY3MVg1U1VGYlE4NkdfVG9rZW46QlFycGJvRHJNb1lTMEh4NzdmMmNRWTJDbkhnXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

小车轮子用于体现urdf中continuous的效果，就是一个中空的圆盘，虽然我们实际用到4个轮子，这里实际建模一个就好。

伸缩臂arm

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MDIxZWU0YmRhOTAwZDBhODdjY2MxMzJlMzQxODZiYmFfeHRvMzNOa0FxMnM3Z0xJeFdnbUJIaldhWEhGWkpneE9fVG9rZW46SmJTVGJFOVNNb0M1dTF4aFY1eGNoWUtwbmVyXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

伸缩臂用于体现urdf中prismatic的效果就是一个长方体，一端打了个圆孔方便夹爪的定位。

夹爪gripper

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MjM5MzBhYWMxNmExMjdjOGEyYTFmZDNhNmEwNTdiYzhfOGcwdVdvQjdiMHo3OVJOZTYzb2wxd2hDOHFISnJKZTJfVG9rZW46SFBNWmJHeTI4b1lBS2p4bllZMWNYbWRnblJmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

这个夹爪略显抽象，不过建模这个夹爪主要是用于体现urdf中revolute，也还算凑合。一端引出的圆柱用于与伸缩臂的圆孔配合，实现定位。

2.2小车整体装配

按照零件以及我们设想的装配，最终的装配结果如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MTUyYTZjNmQ4NTAzZDk4YjQyNzcwMzgwMTI1NGY2MmRfMEl1Nmp4dkNxMFZzQnVDd2ZYNHoxS1gwZmN5dXNFMjZfVG9rZW46WVBwcWJuTDZ4b0JwdnJ4aUxUNGNOWkhHbnlmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

各构件的运动关系如下图表示

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NmJjMGQ2M2Q0NmZlNTJiYWRmMmRhMGZhYzhmNjc0MTFfT2FDNjhrOXdzM0Z2UUthcDlKbWhOZVJqb2Q2NnJwVktfVG9rZW46R1pNdWJ3ZDRwbzdwdU14ejZMcmNwRGxpbkZjXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

# 三、为装配体标注参考坐标系和参考轴

## 3.1.为什么要为装配体标注参考坐标系和参考轴？

观察urdf中定义关节的代码段

```xml
<joint name="front_left_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="front_left_wheel"/>
  <origin xyz="0.2 0.15 0" rpy="1.5708 0 0"/> 
  <axis xyz="0 0 1"/> 
</joint>
```

`<origin xyz="0.2 0.15 0" rpy="1.5708 0 0"/> `定义了子连杆的坐标系原点（通常也是关节的坐标）

`  <axis xyz="0 0 1"/>  `则定义该关节是绕着（沿着）哪根轴运动的。

在装配体中标注参考坐标系和参考轴实际上就是将上述urdf代码可视化手写了一遍，这是必要的。

## 3.2.需要标注多少个参考系和参考轴？

这个是根据机器人的关节总数决定的，有$$n$$个关节，就需要建立$$n$$个参考坐标系和$$n$$个坐标轴，外加一个base的参考坐标系。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=Y2Q5ZmJmMTc5NjMxYmE4MDhlM2UwZThiZjFjODIwOWNfejFuQW82NXg1ejlWTmRLNGlqMk9sREtSY2ZEejB6ME5fVG9rZW46V0pwT2J0ZVVRb0ZVaHR4N2xOQmNWSjlmbnFkXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

参考我们小车的机器人运动学树，其中的每一个箭头就代表一个关节，我们总共需要建立6个参考坐标和参考轴，外加一个Base的参考坐标系。

## 3.3.如何标注参考系和参考轴

建立参考坐标系我们可以遵循以下步骤:

**①建立参考轴**

这一步比较简单，对于旋转运动（如小车轮子），绕着哪个轴旋转，这就是我们的参考轴；对于平移运动（如伸缩臂），沿着哪个轴移动，这就是我们的参考轴

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTc4NDVmNWU4YTcwNzRiMTE2MzQ4Yjg0ZGYxMmU0YmNfQ20yTWd2UVJ2dkFNUGJ3akVFcFFxREtlQXBOZmlpZ01fVG9rZW46QUUwU2I3bWxzb1NQUXd4T0V2c2NuTmtJblRnXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

在s&#x77;**“参考几何体”**&#x9009;项卡选&#x62E9;**“基准轴”**&#x5373;可创建参考轴，按照引导即可在对应位置创建参考轴

车轮的参考轴建立如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MGM4ZjhjYzc1NmVlNjg4NTlmMjdmMDZjOWNiYmFiNTlfNEtUSzdIbXdmRUQxczRIaVdqRWVjSnhhMXlQaktweW9fVG9rZW46RUhMYWIwQlBJb0xQV0F4MWVFMGNpV3l2blZoXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

伸缩臂建立基准轴如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTAzZjljZTk0N2FhZmNkMzMwMjc0YmEyZjY2YzhkMjJfUHlmVkNmOUZvR1Q5VXp0NktQaGxvMExCWXpYN2NGRjJfVG9rZW46TzcxSWJYYkxob1h1TTd4WXpQT2MxZ29XbjhiXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

注：建立伸缩臂的参考轴稍微麻烦点，推荐使用点和基准面的建立方式，在伸缩臂中心取一个点，然后再取合适的平面，即可建立一条过伸缩臂中心的参考轴

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MjRiM2U4OTUzMmQ2NTlhNjkwODgwMzJlNTM1YmU0NGRfS3BJOVVTcnpwdWY1dlVNc3QwUUVVVVYySURKT040bE1fVG9rZW46RzJORmJUSzYyb0tESG14djRlcWNGY3hKblJmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

**②取点**

取点方法是“参考几何体”——“点”

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTgyYzUyYzkyOTYwY2M5ZDZkOWUwMDM1ZGYzNTY2NmVfT1BIMzZKZmY0cnR6Ym9VQ1lUcVJyYTh0b3BYS1JoYnNfVG9rZW46UkE5emJvdkZlb2FGRUd4Y1NtUWNDS3pRblZlXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

a.取点是为了确保参考坐标系处于正确的位置，通常这个点位于父连杆和子连杆相连接的关节的中心上

b.这个点通常点在父连杆上

c.坐标系的Z与实际旋转轴和

比如：

**对于车轮wheel**，其与底盘相连接的关节位于图中箭头的指示位置，我们可以在这个位置，在父连杆上取一个点。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDFjODUwMjNkMjZlMGFjNDBmNmM4YTQ3ZmNiMzVjZTFfWUdraHJHSGV1bXQ3bFRQc1hDOWloaFRINmhJZGR6bWRfVG9rZW46VG1YcWJYRkZvb1FWckd4Yjd5R2M5eXRrbkNjXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)



![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=YzM1NjBlOThhMDBmNzg4N2JiZDkxNzUzYTkzODAzMDlfVXRHU3NkWk9qWEhCeFd1VmlRRGdJcklKdXliN2pRT3dfVG9rZW46QzRCR2JXWEJYb3lzWXp4QTdSZ2NFUk5ObkVmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

随后在“参考几何体”——“坐标系”建立参考坐标系

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=YWNmYThiNjYyMmIwMTQ2NGYwY2YzZDVhNjFjYTBiMmRfSUJGckRxNlVnbEN6QWdNWkhIakxhNlZDbGtJdG1FTGFfVG9rZW46UkZZcWJKY2ltbzJFS3B4c3NIemNDdkpKblNmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

坐标系的取点选择我们刚取好的**点11**，Z轴选择之前建立的**参考轴wheel\_axis，**&#x78;轴和y轴的方向符合右手定则即可(在SW上保持默认）。

**对于伸缩臂arm**

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDFmM2RlMjIxOWZlZmQ1MjE3ZTdhNzE3Y2M1MzU2OTVfcFlyT2NyUko1amlBU1RCYjhDNVRESTJVMHpTOHpZQ3JfVG9rZW46VldDMWIyUTBpb3ZoREd4OHcxWmNjQ05XbmNnXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

随后依次建立各个参考轴和参考坐标系如下，7个参考坐标系和6个参考&#x8F74;**<span style="color: inherit; background-color: rgba(183,237,177,0.8)">（请一定要用英文命名好！！！）</span>**

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjExN2EzODU0MDA2NDVhMWE2ZjMxZGY2MTk4NmYwMzlfR3RhTEdkb2hHeHRrZHpqdnM1Vm9aUkVDdDQzWDJQWkJfVG9rZW46UWVDRGJPRVNyb0p0VHJ4VWVra2NHdzRHbmZiXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

# 四、配置导出urdf选项卡

4.1打开导出urdf文件配置界面

在SW界面**工具**——**Tools**——**Export as URDF**打开URDF导出配置界面

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=OTdiZWVhNjk0NGJjZWJkM2VmOWFkNjgzZDhhYTUzOWZfSFJxdmVqRE5KRTA0M0k0OG9FbWdiMjZKcm8zZ2l0R0ZfVG9rZW46VHBPN2JsS3kwb2NvSWZ4eGJpMWN2aDlBbmJoXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

打开的界面如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=OTBhOTAyOTgyMmEwMDU1YmM1MTJmOGFmZDg3NWVkNmNfMUk5ZGZYYlZsR1hUNjNiaVFiT3htNUE0ZlVnNHY5cDNfVG9rZW46SnJVamJGTkZMb3Zzenl4eUZGc2N5TjZDbk1jXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

第1个选项框表示配置当前连杆的名字

第2个选项框表示配置当前连杆的参考坐标系

第3个选项框表示配置属于当前连杆的实际建模

第4个选项框表示配置该连杆下有多少个子连杆

对于我们的小车底盘base，其下有5个子连杆，我们可以这样配置。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NTIyMzhhODdlZTk5MTY0MGZkZGYzOWJmNDZiNjJhMjNfRU9nZkdVT1BBTGF3V2hqQXN4cHVVempPdVdqZmFMRmxfVG9rZW46V21Fb2I2VlUzb3JuRnl4SGtqcWNyNU9rbjNkXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

可以发现，左边的分支树多了5个Empty\_Link，我们点击任意一个Empty\_Link，得到界面如下：

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZmQwOWE0YTZhZDZlOTI4OTRkOGI1NzQ5OGMwOTJmOTVfNHYydEhBN3QyazZPWjFaV3I2aklvUGpvWndKbmpNd3ZfVG9rZW46Rzl2UmJrNlhpb2l6TUJ4T3p0SmNzVkg5bkJmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

第1个选项框表示配置当前连杆的名字

第2个选项框表示配置当前连杆和父连杆之间关节的名字

第3个选项框表示配置当前连杆的参考坐标系

第4个选项框表示配置当前连杆运动的参考轴

第5个选项框表示配置当前连杆的关节类型

第6个选项框表示配置当前连杆的实际建模

第7个选项框表示配置当前连杆下有多少个子连杆。

需要特别注意的是**第5个选项框表示配置当前连杆的关节类型**

选择什么样的关节类型可以根据以下表格确定：

比如对于wheel我们这样配置，由于我们已经提前配置好了参考坐标系wheel和参考坐标轴wheel\_axis并命名好，这一步比较轻松，注意选择wheel对应的关节类型是continuous就好

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MGI4YmQ3MGQxZWMyNWFhYWI4MTc0MDE3YjlhNTJiM2RfcThzZWZUdUw2c2RLRUZGTGZ4a29oOVNZakxURjFPTGNfVG9rZW46TFpFVmJoMXc4bzBLTDd4QUpmemNQbWd1bkVlXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

arm的配置如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZmJkNzFlM2U2MGEyMTdjN2U5MzkzNDFmMzVlZWY4N2Rfb2c0aXQ5QUFJaFVYeXhac3dLOWt1ZWh6SkZNd2tNZGhfVG9rZW46UUtscGJUSnR1b3BETmR4Y0syU2NlWks5bnhCXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

gripper的配置如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=M2UyMWU5MmRkMzIzODNiYzhhYzVmNjFmMzE3MjYyOTdfeXpaVFkwT1NpUHhSUUJNYmpqRlg5VTdhR0hOa0owOXdfVG9rZW46UksyZWJXS29Ib2libTN4bjJFMGNQd2JwbjcwXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

最后的urdf树如下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MmVlOGM5ZjQzMTAwMzU1OWE2MWEyMWI0NDFlMzQ2Y2RfYzFOYUV1YVk5dEhobktYY3kxTHpVSHd3Wk92aTlzNTNfVG9rZW46T2VKT2JBNnlUb1JsMHJ4WVIxWWMxcFpjbkxnXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

这个时候就可以点击“Preview and Export”进行导出

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ODEzMjRkM2IwZGQwY2NkMDJiZWYwNWM4NjU2NDM2NjFfbW1uUk53WTFJa1U4aVpBWmFkSXF6cE9Pb3Z4aXZFb3ZfVG9rZW46RzlzRmJSSWtjbzZXWWp4d29ENGNQaWVYblRjXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

打开的界面如下：

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NmMxNjEzZWQxZjJmMmEzYjE1NGMyYzY1NDgwYzQ4NTVfandtR3FMNHJzME1uRWlVclRFcFIwMkVyY3pVUUdvS1dfVG9rZW46Qm5QYWJOZHVsb1VMa3d4VHdUa2NndnRkbnViXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

首先进入的是关节配置界面，点开左边任意joint查看，发现sw2urdf已经自动帮我们配好了Origin和Axis，这些数据都是基于我之前配置好的参考坐标和参考轴生成的。

值得注意的是，arm的关节类型prismatic是和gripper的关节类型是revolute，这两个类型的Limit需要我们自己配置，点开arm\_Joint和gripper\_Joint进行配置

**arm\_Joint配置如下**

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=Yjk5ZTNiNzBjMzU5N2ExMGMwYzM2ZWNiMDgzYzk5ZDZfSVRJZ25Fd3FqUnM5cnk1Q2lkcHZiMTBQY3ZlUzZLWkdfVG9rZW46V2lRZ2JlOXlsb2ZBSHF4QmZsTWM0Wnk0bnRoXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

lower（位置最小值），这里我配置-0.03m

upper（位置最大值）,这里我配置0.00m

effort（最大推力），这里我配置20N

velocity(最大速度），这里我配置1m/s

大家根据自己的实际情况配置即可

**gripper\_Joint的配置如下**

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NTQ0NmM3M2ZkYzJkNGY2ODg0Zjc5NDNiMmQ2OTBmMGJfdzJieVlieEtVZHc5cWMxVWx3dmZpUmJSaWg3bkYyQlJfVG9rZW46UDdkS2J6dnZsb0wwZnR4bGR5Y2M0RHJqbnZjXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

随后点击右下角的**Next**，来到连杆配置界面

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MzNmMmU0NjhmZjAzNTMxYjNmNDY3NjJjMjk1MmVjODlfcGZEcWpUMkN6NTYzOE5aR1Y3Q29SbE1zVmJqa3JvSVhfVG9rZW46SHJBNmJ4RHB1b1BBU2Z4bVp1TmNtbkd6bmRjXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

sw2urdf已经自动根据我们连杆的实际建模和实际使用材料（在SW中进行材料配置）帮我们计算好了质量，转动惯量等动力学参数，我们保持默认即可，读者也可以根据自己的需要进行修正。

我们选择右下角**Expoer URDF and Meshes**保存文件

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=YjQ4MGRjYzRjNGUzNTkwMGE2ZWVlZDg4OWY1MmM2N2JfZng4S0ZaQVFVeTVPeXVZMldENXo4N2FEeDlLMWl4YzdfVG9rZW46WkxEQWJQaURlb2NPRGd4a1NqdWMyTU96bmNlXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

笔者将文件命名为car.SLDASM保存在了调试pybullet的工程目录下

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=NzM0ZTQyYTZiOGZhYzI0NDYyZGJhNWNkZmZlMTE0NTdfWU13akhyTFY5czBGR1FmMGxieFh3WUkwUHVQdDd6MjFfVG9rZW46SkxjMGJDVkpVb1ZsTW14OFc1YWNneEZKbmxkXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

# 五、在pybullet打开导出好的小车urdf文件

导出的car.SLDASM文件内容如下，urdf文件夹就保存着我们需要的.urdf文件，meshes文件夹下保存着实际建模的.stl文件，也很重要。

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=YjEyZjI5MTg0YzY4NWU3MzA3ZDg1ZDcwYTBmOThjNGNfVUNZSndzV2pTaGM5cW9id0t4VldIVXVYU0R2M1RtNzVfVG9rZW46RWlqcGI4T0tGb3FCYUp4NVp1OGNXaEhObkZmXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ODZlMWZiZTZhMDBjOGFkYzUyYWNhMzJjNDRmMWJjYjRfc1NIcGFSbzFFZGlJWmFNbnByZERlQ0Y4cVd1d1hpZDlfVG9rZW46T29DcmJvczFDb3pkdER4NDZMNWNVTDIwbklnXzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=MzMxYmU1NmE4YjIxNTA1MzIwZDEzNTg0MDlmNzgzZWZfU1dMWm16VUFSZ1A1VnN3enVpNVVpSG9jdzVNeDdqMUxfVG9rZW46S0lOZWJpMloxb2lmamV4VWE4RmNLTUc1bmR6XzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

在工程文件下编写测试代码**cat\_test.py**，内容如下：
请保证`cat_test.py`和`car.SLDASM`在同一目录下

```python
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
```

运行程序效果如下：

![](https://bcn2kciybq52.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGVjNDdkODg0YjVjMzYzMjVkZmY0Y2YwNjEyODA3MTNfcktPbDRLbWNuQmtrdEdUb2xWUG9hNkFQR01YV1ZhRlhfVG9rZW46TmNheWI1amlwb05kbWl4UVdmY2NzdG9rbjZ6XzE3Njg3MTk4NTE6MTc2ODcyMzQ1MV9WNA)

不知道为什么这个gripper位置反了（= =，摆烂了不管了）

右边有三个滑块分别是速度控制滑块，arm伸缩滑块和gripper转动滑块，读者可以自由拖动试试。

至此，我们顺利地将小车的SW建模导出成urdf，并在pybullet里导入并实现简单的控制。
