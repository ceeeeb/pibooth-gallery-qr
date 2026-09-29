#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os.path as osp
from setuptools import setup


HERE = osp.abspath(osp.dirname(__file__))

with open(osp.join(HERE, 'pibooth_gallery_qr.py'), encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', f.read()).group(1)


setup(
    name='pibooth_gallery_qr',
    version=version,
    description="Pibooth plugin: QR code on wait screen pointing to a local gallery service",
    long_description=open(osp.join(HERE, 'README.rst'), encoding='utf-8').read(),
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
    ],
    author="Christophe",
    url="https://github.com/ceeeeb/pibooth-gallery-qr",
    download_url="https://github.com/ceeeeb/pibooth-gallery-qr/archive/{}.tar.gz".format(version),
    license='MIT license',
    platforms=['unix', 'linux'],
    keywords=['Raspberry Pi', 'photobooth', 'gallery', 'qr'],
    py_modules=['pibooth_gallery_qr'],
    install_requires=[
        'pibooth-ceeeeb>=2.0.9',
        'qrcode>=6.1',
    ],
    zip_safe=False,
    entry_points={
        'pibooth': ["pibooth_gallery_qr = pibooth_gallery_qr"],
    },
)
