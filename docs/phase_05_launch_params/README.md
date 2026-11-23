# Phase 5 — Create the parameter and launch file 

In this phase we are turning the hardcoded thresholds in the Phase 4 nodes into configurable parameters and starting both nodes with a single launch file, we create first the nodes without the parameter to ensure it's working without parameter and we add them now.

-------------------------------------------------------------------------------------------------------
##Steps

### Step 1: Create  the parameterized node Control_node_params and Actuator_node_params
1.1 Create the nodes inside **my_py_pkg** as we did in phase 4.

1.2 Copy the code from  Control_node_params.py  and Actuator_node_params in ros2_workspace and save.

1.3 Declare parameters (in __init__, before using any parameter):

```
self.declare_parameter('safety_distance', 10.0)
self.declare_parameter('max_distance', 50.0)
self.declare_parameter('max_speed', 200)
```

declare_parameter() declares the parameter, and the value can be set through the launch file or the command line; to make runtime changes take effect, the latest value must be retrieved inside the callback using get_parameter()
then get them at the beginning of  **callback_print_distance** in Control node and in **evaluate** in Actuator node (in Actuator node we need just the safety and max distance).
```
self.safety_distance = self.get_parameter('safety_distance').value
self.max_distance = self.get_parameter('max_distance').value
self.max_speed = self.get_parameter('max_speed').value
```
This is necessary due declare_parameter() tells ROS 2 that the node expects a parameter with that name and provides a default value. Without declaration, get_parameter() will not work . Reading the value again inside the callback ensures that when you run ros2_param_set at runtime, the node immediately uses the new value, rather than only reading it once at startup .



### Step 2: Create the YAML parameter file
Create a config/ folder in the package root directory and write params.yaml:
```
cd /ros2_ws/src/my_py_pkg
mkdir -p config
```
Then a file **params.yaml** inside the config and contain 
```
control_node_params:
  ros__parameters:
    safety_distance: 10.0
    max_distance: 50.0
    max_speed: 200

actuator_node_params:
  ros__parameters:
    safety_distance: 10.0
    max_distance: 50.0
```
The top-level key in the YAML must exactly match the node name set in super().__init__("control_node_params").




### Step 3:Create the launch file
Create a launch/ folder in the package root directory with name **project_01.launch.py** , ad the code form the **ros_ws/my_py_pkg/launch/project_01.launch.py**
When the launch file starts the node, ROS 2 reads the YAML file, finds the parameter group with the matching node name, and injects those values . get_package_share_directory finds the installation path of the package, ensuring the YAML file can be located after colcon build ,if the node name passed through the name parameter in the launch file does not match the YAML, the parameters will not be loaded.




### Step 4: Update setup.py (entry points + installation rules)

4.1 Open **setup.py** and add the entry points for the 2 new nodes
```
'control_node_params = my_py_pkg.control_node_params:main',
'actuator_node_params = my_py_pkg.actuator_node_params:main',
```

4.2 In setup.py update also the **data_files** add

```
(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
(os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
```

data_files in setup.py is responsible for installing the launch/ and config/ directories into the package's share directory, so that get_package_share_directory('my_py_pkg') can find them after colcon build. Without this step, the launch file will report "file not found".

Also add **import os** and **from glob import glob** at the top of setup.py (if not already present). Without this step, get_package_share_directory will not find the YAML file, and the launch will fail.




###Step 5: Build and test

```
cd /ros2_ws
colcon build --packages-select my_py_pkg
source install/setup.bash
```

#### Test A --  Launch file starts both nodes:

```
ros2 launch my_py_pkg project_01.launch.py
```
You should see both nodes' startup logs. 
In another terminal, check:
```
ros2 node list        # should show /control_node_params and /actuator_node_params
ros2 param list /control_node_params   # should show the three parameters
```

#### Test B — Verify parameters are loaded:

```
ros2 param get /control_node_params safety_distance
```
Expected output: Double value is: 10.0. If it returns 10.0, the YAML was loaded successfully.


#### Test C — Runtime parameter change (the core of Phase 5):
While the launch is running, in another terminal:
```
ros2 param set /control_node_params safety_distance 20.0
```
Then publish a distance of 15 cm:
```
ros2 topic pub /distance example_interfaces/msg/Float32 "{data: 15.0}" --once
```
Before the change: 15 cm > 10 cm safety distance, speed should be nonzero. After the change: 15 cm < 20 cm, speed should be 0. If the Actuator Node also reads the parameter, its status should become [STOP]. This proves the parameter system works end to end.


-------------------------------------------------------------------------------------------------
## What I Learned
- The role of declare_parameter(): it tells ROS 2 that the node will use this parameter, and the type is inferred from the default value .

- The timing of get_parameter(): it can be called once in __init__, or it can be called on every callback to support runtime changes.

- The matching relationship between the YAML file and the node name: the top-level key must equal the node name in super().__init__() or the name in the launch file.
