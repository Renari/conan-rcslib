from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class RcslibConan(ConanFile):
    name = "rcslib"
    description = "Keep it short"
    topics = ("conan", "rcslib")
    url = "https://github.com/Renari/conan-rcslib"
    homepage = "https://github.com/usnistgov/rcslib"
    license = "NIST"
    generators = "make"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = ()

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):

        tools.get("https://github.com/usnistgov/rcslib/archive/rcslib-{0}.zip".format(self.version))
        extracted_dir = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

            
    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)

            self.run("chmod a+x configure")

            os.makedirs('pkgconfig')
            pkg_config_path = os.path.abspath('pkgconfig')
            pkg_config_path = tools.unix_path(pkg_config_path) if os.name == 'nt' else pkg_config_path

            autotools.configure(pkg_config_paths=[pkg_config_path])
            autotools.make()
            autotools.install()

    def package(self):
        self.copy(pattern="license-NIST.txt", dst="licenses", src=self._source_subfolder)

        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        libs = tools.collect_libs(self)
        # remove invalid Makefile.lib files
        self.cpp_info.libs = [ x for x in libs if "Makefile" not in x ]
