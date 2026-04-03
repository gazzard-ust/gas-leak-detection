from setuptools import find_packages, setup

package_name = 'MEx3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={
        package_name: ['*.pt', '*.png'],
    },
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gazzard-ust',
    maintainer_email='gazzard-ust@users.noreply.github.com',
    description='Gas leak detection and localization via CO2-guided crack inspection',
    license='MIT',
    entry_points={
        'console_scripts': [
            'image_publisher = MEx3.image_publisher:main',
            'image_subscriber = MEx3.image_subscriber:main',
            'gazzard_gui = MEx3.gazzard_gui:main',
            'gazzard_gui_v2 = MEx3.gazzard_gui_v2:main',
            'gazzard_gui_v3 = MEx3.gazzard_gui_v3:main',
            'gazzard_gui_detection_final = MEx3.gazzard_gui_detection_final:main',
            'turtlebot_publisher = MEx3.turtlebot_publisher:main',
            'laptop_subscriber = MEx3.laptop_subscriber:main',
            'senseair_s8_publisher = MEx3.senseair_s8_publisher:main',
        ],
    },
)
