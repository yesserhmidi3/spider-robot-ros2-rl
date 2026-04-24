from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'spider'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Include URDF files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # Include Mesh files
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        # Include config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yesser',
    maintainer_email='yesser.hmidi3@gmail.com',
    description='Spider robot description and simulation',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'control_node = spider.control:main',
            'train_node = spider.train:main',
        ],
    },
)
