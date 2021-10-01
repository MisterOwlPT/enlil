# Enlil
#
# Copyright © 2021 Pedro Pereira, Rafael Arrais
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import setuptools

with open('./README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='enlil',
    version='1.1.3',
    author='Pedro Melo, Rafael Arrais',
    author_email='pedro.m.melo@inesctec.pt, rafael.l.arrais@inesctec.pt',
    description='Automatic containerization of complete ROS workspaces.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/MisterOwlPT/enlil',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[
        'docopt',
        'jinja2',
        'pyyaml'
    ],
    py_modules=['enlil'],
    entry_points={
        'console_scripts': [
            'enlil=enlil:main'
        ]
    },
    include_package_data=True
)
