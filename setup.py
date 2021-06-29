import setuptools

setuptools.setup(
    name='enlil',
    version='1.0.0',
    author='Pedro Melo',
    author_email='pedro.m.melo@inesctec.pt',
    description='Automatic containerization of complete ROS workspaces.',
    license='Apackage License 2.0',
    packages=setuptools.find_packages(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[
        'docopt',
        'jinja2'
    ],
    py_modules=['enlil'],
    entry_points={
        'console_scripts': [
            'enlil=enlil:main'
        ]
    },
    include_package_data=True
)
