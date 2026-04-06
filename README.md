# Project 8, ROS2 Navigation Stack, Group 1
#### Progress Munoriarwa & Malcolm Benedict

### Part 1

Using the recommended parameter ranges, nine total sets of parameters were examined, representing all combinations of the three radii and scaling factors. The inflation radius governed how far from a detected obstacle the cost would be increased. A large radius would result in the movement cost of a space being altered even a significant distance from the object itself. The scaling factor determined how the cost within the radius scaled. Therefore, the cost of any given space was based on its relative position within the radius and the scaling factor.

<div style="text-align: center; margin-left: auto; margin-right: auto; width: 75%">

**Baseline**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 3.0                 | 0.70             |
![alt text](./figures/bTest0.png "Baseline")

**Test 1**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 2.0                 | 0.70             |
![alt text](./figures/bTest1.png "Test 1")

**Test 2**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 5.0                 | 0.70             |
![alt text](./figures/bTest2.png "Test 2")

**Test 3**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 3.0                 | 0.15             |
![alt text](./figures/bTest3.png "Test 3")

**Test 4**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 3.0                 | 0.45             |
![alt text](./figures/bTest4.png "Test 4")

**Test 5**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 2.0                 | 0.15             |
![alt text](./figures/bTest5.png "Test 5")

**Test 6**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 5.0                 | 0.15             |
![alt text](./figures/bTest6.png "Test 6")

**Test 7**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 3.0                 | 0.45             |
![alt text](./figures/bTest7.png "Test 7")

**Test 8**
|`cost_scaling_factor`|`inflation_radius`|
| :-----------------: | :--------------: |
| 5.0                 | 0.45             |
![alt text](./figures/bTest8.png "Test 8")

</div>

Route planning was done with Test 8 parameters. However, the robot never moved, even with a valid path to target and an initial pose estimate. Nav2 would show that it was attempting to follow the path, but no actual movement happened. This was even after the initial pose estimate had been set, and the Turtlebot moved around with teleop. This issue had been encountered in previous Turtlebot experiments, however, the author cannot remember how they resolved the issue.

<div style="text-align: center; margin-left: auto; margin-right: auto; width: 75%">
![alt text](./figures/navGoal1.png "Nav2 Goal")
</div>


Next, the obstacle layer parameters were varied, and a human was introduced to the environment to see the effects on the cost map. The obstacles max range parameter governed the range at which obstacles should be detected, while the raytrace max range parameter governed obstacle clearing distance. Unfortunately, no meaningful difference could be observed.

<div style="text-align: center; margin-left: auto; margin-right: auto; width: 75%">

**Baseline**
|`raytrace_max_range`|`obstacle_max_range`|
| :----------------: | :----------------: |
| 3.0                | 2.5                |
![alt text](./figures/cTest0a.png "Baseline, no human")
![alt text](./figures/cTest0b.png "Baseline, with human")

**Test 1**
|`raytrace_max_range`|`obstacle_max_range`|
| :----------------: | :----------------: |
| 1.5                | 1.25               |
![alt text](./figures/cTest1a.png "Test 1, no human")
![alt text](./figures/cTest1b.png "Test 1, with human")

**Test 2**
|`raytrace_max_range`|`obstacle_max_range`|
| :----------------: | :----------------: |
| 6.0                | 5.0                |
![alt text](./figures/cTest2a.png "Test 2, no human")
![alt text](./figures/cTest2b.png "Test 2, with human")
</div>

## Part 2 — Keepout and Speed Filter Zones
### The taped floor zones
![alt text](./figures/taped_floor.jpg "The taped floor zones")
### Keepout zone rendered
![alt text](./figures/keepout_render.png "Keepout zone rendered")
### Routes around the keepout zone
![alt text](./figures/keepout_path.png "Routes around the keepout zone")
