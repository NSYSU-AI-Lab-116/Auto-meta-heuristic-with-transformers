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

    try:
        print("\n\nCompiling the project...")
        build_dir = os.path.join(os.getcwd(), "src", "cpp", "build")

        if os_info["name"] == "posix":
            shutil.rmtree(build_dir, ignore_errors=True)
            os.system("cmake . && make -j")
        elif os_info["name"] == "nt":
            shutil.rmtree(build_dir, ignore_errors=True)
            os.system("cmake . && make -j")

        open(os.path.join(build_dir, "__init__.py"), "w").close()
        print("C++ extensions compiled successfully.")
    except Exception as e:
        print(f"Error during compilation: {e}")
        print("Compilation failed. Please check the logs for more details.")