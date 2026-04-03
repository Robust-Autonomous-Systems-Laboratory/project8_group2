# Project 7, ROS2 Navigation Stack, Group 1
#### Progress Munoriarwa & Malcolm Benedict

1a & 1b

Cost Map values:
    Test 0 (Baseline):
        cost_scaling_factor: 3.0
        inflation_radius: 0.70

    Test 1:
        cost_scaling_factor: 2.0
        inflation_radius: 0.70

    Test 2:
        cost_scaling_factor: 5.0
        inflation_radius: 0.70

    Test 3:
        cost_scaling_factor: 3.0
        inflation_radius: 0.15

    Test 4:
        cost_scaling_factor: 3.0
        inflation_radius: 0.45

    Test 5:
        cost_scaling_factor: 2.0
        inflation_radius: 0.15

    Test 6:
        cost_scaling_factor: 5.0
        inflation_radius: 0.15

    Test 7:
        cost_scaling_factor: 3.0
        inflation_radius: 0.45

    Test 8:
        cost_scaling_factor: 5.0
        inflation_radius: 0.45

    Route planning was done with test 8 prams. Robot never moved, even with a valid path to target and an initial pose estimate.


1c

Obstacle Layer
    Test 0 (base):
        raytrace_max_range: 3.0
        raytrace_min_range: 0.0
        obstacle_max_range: 2.5
        obstacle_min_range: 0.0
    Test 1:
        raytrace_max_range: 1.5
        raytrace_min_range: 0.0
        obstacle_max_range: 1.25
        obstacle_min_range: 0.0
    Test 2:
        raytrace_max_range: 6
        raytrace_min_range: 0.0
        obstacle_max_range: 5
        obstacle_min_range: 0.0