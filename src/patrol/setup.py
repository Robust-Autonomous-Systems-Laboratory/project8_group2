from setuptools import find_packages, setup

package_name = 'patrol'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='progress',
    maintainer_email='mmunoria@mtu.edu',
    description='Autonomous patrol package for EE5531 Project 8',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test.py = patrol.test:main',
            'patrol_node.py = patrol.patrol_node:main',
        ],
    },
)
