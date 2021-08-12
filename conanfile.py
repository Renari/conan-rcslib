from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class RcslibConan(ConanFile):
    name = "rcslib"
    description = "NIST Real-Time Control Systems Library including Posemath, NML communications & Java Plotter"
    topics = ("conan", "rcslib")
    url = "https://github.com/Renari/conan-rcslib"
    homepage = "https://github.com/usnistgov/rcslib"
    license = "NIST"
    generators = "make"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = ()

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.Git().clone("https://github.com/usnistgov/rcslib.git", "master")
        tools.Git().checkout(self.version)

    def build(self):
        self.run("chmod a+x configure")

        os.makedirs('pkgconfig')
        pkg_config_path = os.path.abspath('pkgconfig')
        pkg_config_path = tools.unix_path(pkg_config_path) if os.name == 'nt' else pkg_config_path

        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(pkg_config_paths=[pkg_config_path])
        autotools.make(["-j1"])  # a race condition will occur when building on more than one core
        autotools.install()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self.build_folder)
        with tools.chdir(self.package_folder):
            tools.remove_files_by_mask("lib", "*.la")
            tools.remove_files_by_mask("lib", "*.lib")
            tools.rmdir(os.path.join("lib", "pkgconfig"))
            if self.options.shared:
                tools.remove_files_by_mask("lib", "*.a")
            else:
                tools.remove_files_by_mask("lib", "*.so")

    def package_info(self):
        self.cpp_info.libs = ["posemath", "rcs"]
        self.cpp_info.names["cmake_find_package"] = "rcs"
