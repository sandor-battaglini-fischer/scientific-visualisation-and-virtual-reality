import vtk

def get_vtk_version():
    version = vtk.VTK_VERSION
    print(version)
    return version

if __name__ == "__main__":
    get_vtk_version()