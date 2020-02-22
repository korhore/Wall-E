#!/usr/bin/env python

from distutils.core import setup
#with open('README') as f:
#    long_description = f.read()


setup(name='Wall-E_Server',
      version='2.0',
      description='Wall-E Robot controlling server',
      author='Reijo Korhonen',
      author_email='reijo.korhonen@gmail.com',

      #py_modules=['Wall-E_Server/Command','Wall-E_Server/Romeo','Wall-E_Server/WalleServer'],
      #py_modules=['Wall-E_Server','Wall-E_Server.Command', 'Wall-E_Server.Romeo', 'Wall-E_Server.WalleServer'],
      #packages = ['Wall-E_Server', 'init'],
      packages = ['Wall-E_Server'],
      package_dir={'Wall-E_Server': 'Wall-E_Server'},
      #package_data={'Wall-E_Server': ['init/Wall-E_Server']},
      #package_dir={'init.d': 'init.d'},
      #data_files=[('/etc/init.d', ['etc/Wall-E_Server'])],
      package_data={'Wall-E_Server': ['../etc/Wall-E_Server',]},
      #package_data={'mypkg': ['data/*.dat']},
      include_package_data=True,
      # 'pyserial', 'pyFirmata', only if you run Robot with arduino, but there is no current imp0lementation yet for that 
      install_requires=['python-daemon',  'lockfile', 'psutil',
                        'python-dev', 'libatlas-base-dev', 'numpy',
                        'pillow',
                        'picamera',
                        'pyalsaaudio', 'tensorflow'],
      url='https://github.com/korhore/Wall-E',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python3',
#        'Programming Language :: Python :: 2.6',
#        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Embedded Systems'
      ],

      scripts=['scripts/setup_service','scripts/Wall-E_Server']
      
      )
