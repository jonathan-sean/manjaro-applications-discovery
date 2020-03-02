import gi
gi.require_version('Pamac', '9.0')
from gi.repository import Pamac


class Get:

    def __init__(self):
        self.config = Pamac.Config(conf_path="/etc/pamac.conf")
        database = Pamac.Database(config=self.config)
        database.enable_appstream()
        self.database = database

    def appstream_category(self, category):
        return self.database.get_category_pkgs(category)

    def all_repo_pkgs(self, title):
        pkgs = []
        for repository in self.database.get_repos_names():
            for package in self.database.get_repo_pkgs(repository):
                icon = package.get_icon()
                if title == "Packages" and not icon:
                    pkgs.append(package)
                elif title == "Applications" and icon:
                    pkgs.append(package)

        return tuple(pkgs)

    def external_repos(self):
        # FIXME some unknown categories are missing
        categories = self.database.get_categories_names()
        return categories, self.database

    def search_single_package(self, pkg_name, pkg_format):

        if pkg_format == "Package" or pkg_format == "Application":
            repo = self.database.search_repos_pkgs(pkg_name)

        elif pkg_format == "Snap":
            repo = self.database.search_snaps(pkg_name)

        elif pkg_format == "Flatpak":
            repo = self.database.search_flatpaks(pkg_name)

        for pkg in repo:
            if pkg_name == pkg.get_name():
                return pkg

        return None