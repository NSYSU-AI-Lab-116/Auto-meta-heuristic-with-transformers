from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import os
import shutil

def compile_cpp_extensions(arg = 'dev'):
    os_info = {
        "name": os.name,
        "system": os.uname().sysname if hasattr(os, 'uname') else "N/A",
        "release": os.uname().release if hasattr(os, 'uname') else "N/A",
        "version": os.uname().version if hasattr(os, 'uname') else "N/A",
        "machine": os.uname().machine if hasattr(os, 'uname') else "N/A"
    }

    print("OS Information:")
    for key, value in os_info.items():
        print(f"{key}: {value}")

    print("\n\nCompiling the project...")
    build_dir = os.path.join(os.getcwd(), "src", "cpp", "build")

    if os_info["name"] == "posix":
        shutil.rmtree(build_dir, ignore_errors=True)
        os.system("cmake . && make -j")
    elif os_info["name"] == "nt":
        shutil.rmtree(build_dir, ignore_errors=True)
        os.system("cmake . && make -j")


class CompileCommand(install):  # Or develop, depending on your needs
    """Custom command to compile C++ extensions during installation."""
    def run(self):
        compile_cpp_extensions('release')
        super().run()

class CompileDevelopCommand(develop):
    """Custom command to compile C++ extensions during develop."""
    def run(self):
        compile_cpp_extensions()
        super().run()

setup(
    name="auto-meta-heuristic",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bp = setup:compile_cpp_extensions',  # Define the 'compile' command
        ],
    },
    cmdclass={
        #'release': CompileCommand,
        'dev': CompileDevelopCommand,
    },
)