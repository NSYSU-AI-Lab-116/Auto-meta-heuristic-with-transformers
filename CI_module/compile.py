import os
import shutil


"""Custom command to compile C++ extensions during develop."""
def compile_ext():
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