from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "V1-README.md").read_text()
setup(name='converter_package',
      version='3.3',
      description='Converter is a reasoning tool designed for the cloud language known as CEAML. CEAML is an extension of TOSCA capable to describe deployment and runtime adaptation for platforms that utilize both Cloud and Edge resources. It can parse CEAML entities and translate them into configuration files for K3s or Kubevirt.',
      author='Giannis Korontanis',
      author_email='gkorod2@gmail.com',
      license='MIT',
      packages=['converter_package'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'pyyaml==5.3.1', 'hurry.filesize==0.9', 'oyaml==1.0'
      ],
      zip_safe=False)
