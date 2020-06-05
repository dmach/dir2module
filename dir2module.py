"""
Recursively read RPMs from DIR or read them from specified pkglist
and generate N:S:V:C:A.modulemd.yaml for them.
"""

import os
import fnmatch
import gi
import hawkey
from dnf.subject import Subject


gi.require_version("Modulemd", "2.0")
from gi.repository import Modulemd


def find_packages(path):
    """
    Recursively find RPM packages in a `path` and return their list
    """
    packages = []
    for _, __, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, "*.rpm"):
            if filename.endswith(".src.rpm"):
                continue
            packages.append(filename)
    return packages


def find_packages_in_file(path):
    """
    Parse a text file containing a list of packages and return their list
    """
    pass


def package_names(packages):
    """
    Takes a list of package filenames and returns a set of unique package names
    """
    names = set()
    for package in packages:
        subject = Subject(package.strip(".rpm"))
        nevras = subject.get_nevra_possibilities(forms=[hawkey.FORM_NEVRA])
        for nevra in nevras:
            names.add(nevra.name)
    return names


def dumps_modulemd(name, stream, version, summary, description, licenses,
                   packages):
    """
    Generate modulemd yaml based on input parameters and return it as a string
    """
    mod_stream = Modulemd.ModuleStreamV2.new(name, stream)
    mod_stream.set_version(version)
    mod_stream.set_summary(summary)
    mod_stream.set_description(description)

    mod_stream.add_module_license("MIT")
    for pkglicense in licenses:
        mod_stream.add_content_license(pkglicense)

    for package in packages:
        component = Modulemd.ComponentRpm.new(package)
        component.set_rationale("Present in the repository")
        mod_stream.add_component(component)

    index = Modulemd.ModuleIndex.new()
    index.add_module_stream(mod_stream)
    return index.dump_to_string()



def dump_modulemd(*args, **kwargs):
    """
    Generate modulemd yaml based on input parameters write it into file
    """
    pass


def main():
    path = os.path.expanduser("~/rpmbuild/RPMS/")
    packages = find_packages(path)
    pkgnames = package_names(packages)

    yaml = dumps_modulemd("foo", "bar", 123, "Summary and stuff",
                          "description should be autogenerated",
                          ["MIT"], pkgnames)
    print(yaml)


if __name__ == "__main__":
    main()
