from distutils.core import setup, Extension
setup(name='Wall-E_Server',
      version='1.0',
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
      #data_files=[('/etc/init.d', ['init/Wall-E_Server'])],
      scripts=['scripts/setup_service','scripts/Wall-E_Server']
      )
