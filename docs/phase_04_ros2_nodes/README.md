# Phase 4 — Create ROS 2 Nodes (Control Node + Actuator Node)

In this phase we create the two Python ROS 2 nodes that form the software
half of the collision-avoidance system. They run on the PC, before the
ESP32 arrives, and are tested with a fake publisher.

## Nodes

- **Control Node** — reads the distance and computes the required speed.
  - Sub: `/distance` (`example_interfaces/Float32`)
  - Pub: `/cmd_speed` (`example_interfaces/Int32`)
- **Actuator Node** — reads distance and speed, prints both, flags a safety
  inconsistency, and provides the data stream for later visualization.
  - Sub: `/distance` (`example_interfaces/Float32`)
  - Sub: `/cmd_speed` (`example_interfaces/Int32`)


> **Note on Ubuntu version:** ROS 2 Jazzy officially targets Ubuntu 24.04
> (Noble). If you are on 24.04, skip Step 1 and install Jazzy natively;
> create a workspace folder on the host and work there.

-------------------------------------------------------

## Steps

### Step 1: Create a container (only if your host is not Ubuntu 24.04)

This project was developed on Ubuntu 25.10 , which is not a
supported platform for Jazzy — `apt install ros-jazzy-desktop` fails on
dependency conflicts. The solution is to run Jazzy inside a Docker
container and **bind-mount a host folder** into it, so all code lives on
the host and can be committed to GitHub.

```
bash
docker run -it \
  --name project_01 \
  -v /absolute/path/on/host:/ros2_ws \
  -w /ros2_ws \
  osrf/ros:jazzy-desktop \
```
 **-v host:container**: code written in /ros2_ws inside the container is
physically stored in the host folder.
  
Verify the distribution:
```
bash
printenv ROS_DISTRO
```
  You must see **jazzy**.
### Step 2: Create the Python package

2.1 Inside **src/**, create the package:

```
bash
ros2 pkg create my_py_pkg --build-type ament_python --dependencies rclpy example_interfaces
```
 Confirm the package exists with ls.

2.2 From the workspace root, build once to confirm the skeleton compiles:
```
bash
cd /ros2_ws
colcon build
```
 

2.3 In VS Code on the host: **F1** → Dev Containers: Attach to
Running Container → select **project_01** → open **/ros2_ws** (if you close the container this connection will be closed also).

### Step 3: Create the Control Node
  
3.1 Enter the inner package folder (the one with the same name as the package):
```
bash
cd /ros2_ws/src/my_py_pkg/my_py_pkg
```
3.2 Create the node file:
```
bash
touch control_node.py
```

3.3 Paste the Control Node code (see control_node.py in ros2_workspace) and save.

3.4 Add the interface dependency to **package.xml**:
xml
```
bash
<exec_depend>example_interfaces</exec_depend>
```
3.5 Register the executable in **setup.py** under **entry_points**:

```
bash
'console_scripts': [
    'control_node = my_py_pkg.control_node:main',
],
```
The format is **executable_name = package_name.module_name:function_name.**
The module name must match the filename exactly, including case.

3.6 From the workspace root, build, source, and run:
```
bash

cd /ros2_ws
colcon build --packages-select my_py_pkg
source install/setup.bash
ros2 run my_py_pkg control_node
```
Expected first log line: **Control node has been started**.

### Step 4: Test the Control Node with a fake publisher

4.1 Open a second shell in the same container:
bash
```
bash
docker exec -it project_01 bash
```
4.2 Source both setups:
```
bash

source /opt/ros/jazzy/setup.bash
source /ros2_ws/install/setup.bash
```
Check the graph:
```
bash

ros2 node list      # should show /control_node
ros2 topic list     # should show /distance and /cmd_speed
```
4.3 Publish a fake distance:
```
bash

ros2 topic pub /distance example_interfaces/msg/Float32 "{data: 25.0}" --once
```
The Control Node terminal prints:

**Distance: 25.0 cm -> Speed: 75**

4.4 Open a third shell (same container) and echo the output topic:
```
bash

source /opt/ros/jazzy/setup.bash
source /ros2_ws/install/setup.bash
ros2 topic echo /cmd_speed
```
Each fake distance publish produces a matching Int32 on /cmd_speed.

### Step 5: Create the Actuator Node

Repeat Step 3 with actuator_node.py and add a second entry point:
```
bash

'console_scripts': [
    'control_node  = my_py_pkg.control_node:main',
    'actuator_node = my_py_pkg.actuator_node:main',
],
```
Rebuild and source before running it.

###Step 6: Verify communication between both nodes

Open three shells in the container, each with both setups sourced:
Shell	|Command
________________________________________________________________________________________
1	    |ros2 run my_py_pkg control_node
2	    |ros2 run my_py_pkg actuator_node
3	    |ros2 topic pub /distance example_interfaces/msg/Float32 "{data: 25.5}" --once


Publish the three test values in shell 3 and observe the other two:

Distance	 |Control Node |	Actuator Node
_____________________________________________________________________
60.0 cm	 |Speed: 200	   |[CLEAR] distance=60.0 cm speed=200
25.0 cm	 |Speed: 75	   |[SLOW] distance=25.0 cm speed=75
5.0 cm	 |Speed: 0	   |[STOP] distance=5.0 cm speed=0

Consistency test: stop the Control Node, then publish a hand-crafted
speed and a critical distance:
```
bash

ros2 topic pub /cmd_speed example_interfaces/msg/Int32 "{data: 150}" --once
ros2 topic pub /distance  example_interfaces/msg/Float32 "{data: 5.0}" --once
```
The Actuator Node prints a warning:
**INCONSISTENCY: distance 5.0 cm but speed 150 != 0**.
This proves the Actuator Node is genuinely monitoring the pair of topics,
not just printing them.

-------------------------------------------------------------------------------------------------
## Problems Encountered and Solutions
- **ModuleNotFoundError:** No module named 'my_py_pkg.control_node'
Cause: the file was named Control_node.py (capital C) while the entry
point declared control_node (lowercase). On Linux, module names are
case-sensitive.
Fix: rename the file to control_node.py and keep the entry point
lowercase (or make both match exactly).

- **AttributeError:** 'function' object has no attribute 'info'
Cause: self.get_logger.info(...) — get_logger is a method and must
be called first.
Fix: self.get_logger().info(...) (with the empty parentheses).

- **ros2 pkg create without example_interfaces**
Cause: the package was created with only rclpy as a dependency, but the
code imports example_interfaces.
Fix: add <exec_depend>example_interfaces</exec_depend> to package.xml.

-------------------------------------------------------------------------------------------------
## What I Learned
- Package structure matters. An ament_python package needs an inner
folder with the same name as the package (my_py_pkg/my_py_pkg/). That
inner folder is the Python module.

- colcon build vs source install/setup.bash. colcon build compiles
and installs the package into install/. Sourcing install/setup.bash
adds that installed package to the current shell's AMENT_PREFIX_PATH, so
ros2 run can find the executable. Both steps are required, in that order.

- The queue-size argument in create_subscription(..., 10) is the QoS
depth: the number of messages buffered if the callback cannot keep up.
10 is a safe default for low-rate sensor data.

- A subscription is bound to one topic. Monitoring two topics requires
two subscriptions.

- Node names vs. executable names. The super().__init__("control_node")
string is the ROS graph node name (/control_node), while the
console_scripts entry is the executable name used by ros2 run. They can
differ, but keeping them identical avoids confusion.

- Docker bind mounts persist code. The -v host:/ros2_ws mount means
code written in the container is stored on the host; deleting the
container later does not delete the code. This is why the GitHub workflow
is unaffected by the container.
