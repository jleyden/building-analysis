from setuptools import setup, find_packages

print(find_packages())
setup(name='dataclient',
      version='0.0.5',
      description='MDAL client v2',
      packages=find_packages(),
      data_files=[('dataclient', ['dataclient/data.capnp'])],
      include_package_data=True,
      zip_safe=False)

