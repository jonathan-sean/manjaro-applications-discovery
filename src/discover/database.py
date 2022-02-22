from Manjaro.SDK import PackageManager
from discover import models, sql, app
from time import strftime
from sqlalchemy.exc import IntegrityError
import json
import multiprocessing



def process(func):
    def proc(*args):
      p = multiprocessing.Process(target=func(*args))
      p.start()
      p.join()        
    return proc


class Database():
    def __init__(self):
        self.pamac = PackageManager.Pamac()

    def reload_tables(self):
        sql.drop_all()
        sql.create_all()
        sql.session.add(
            models.Discover(
                last_updated=strftime("%Y-%m-%d %H:%M")
            )
        )
        sql.session.commit()
       # self.populate_pkg_tables()
        app.config['IS_MAINTENANCE_MODE_PKGS'] = False
       # self.populate_flatpak_tables()
        app.config['IS_MAINTENANCE_MODE_FLATPAKS'] = False
        self.populate_snap_tables()
        app.config['IS_MAINTENANCE_MODE_SNAPS'] = False
      

    @process
    def populate_pkg_tables(self):   
        ignore_list = (
            "picom",
            "pantheon-onboarding",
            "wingpanel",
            "systemsettings",
            "kshutdown",
            "khelpcenter",
            "kinfocenter",
            "gnome-control-center",
            "discover",
            "deepin-control-center",
            "lxappearance-gtk3"
        )     
        for pkg in self.pamac.get_all_pkgs():
            d = self.pamac.get_pkg_details(
                pkg.get_name()
            )
            if d["icon"] and d["name"] not in ignore_list:
                model = models.Apps(
                    pkg_format="native",
                    app_id=d["app_id"],
                    icon=d["icon"].replace('/usr/share/app-info', '/static'),
                    launchable=d["launchable"],
                    title=d["title"],
                    backups=" ".join(d["backups"]),
                    build_date=d["build_date"],
                    check_depends=" ".join(d["check_depends"]),
                    conflits=" ".join(d["conflits"]),
                    depends=" ".join(d["depends"]),
                    description=d["description"],
                    download_size=d["download_size"],
                    groups=" ".join(d["groups"]),
                    #ha_signature=d["ha_signature"],
                    pkg_id=d["pkg_id"],
                    install_date=d["install_date"],
                    installed_size=d["installed_size"],
                    installed_version=d["installed_version"],
                    license=d["license"],
                    long_description=d["long_description"],
                    makedepends=" ".join(d["makedepends"]),
                    name=d["name"],
                    optdepends=json.dumps(d["optdepends"]),
                    optionalfor=" ".join(d["optionalfor"]),
                    packager=d["packager"],
                    provides=" ".join(d["provides"]),
                    reason=d["reason"],
                    replaces=" ".join(d["replaces"]),
                    repository=d["repository"],
                    required_by=" ".join(d["required_by"]),
                    screenshots=" ".join(d["screenshots"]),
                    url=d["url"],
                    version=d["version"]
                )

            else:
                model = models.Packages(
                    pkg_format="native",
                    app_id=d["app_id"],
                    icon="/static/images/package.svg",
                    launchable=d["launchable"],
                    backups=" ".join(d["backups"]),
                    build_date=d["build_date"],
                    check_depends=" ".join(d["check_depends"]),
                    conflits=" ".join(d["conflits"]),
                    depends=" ".join(d["depends"]),
                    description=d["description"],
                    download_size=d["download_size"],
                    groups=" ".join(d["groups"]),
                    #ha_signature=d["ha_signature"],
                    pkg_id=d["pkg_id"],
                    install_date=d["install_date"],
                    installed_size=d["installed_size"],
                    installed_version=d["installed_version"],
                    license=d["license"],
                    long_description=d["long_description"],
                    makedepends=" ".join(d["makedepends"]),
                    name=d["name"],
                    optdepends=json.dumps(d["optdepends"]),
                    optionalfor=" ".join(d["optionalfor"]),
                    packager=d["packager"],
                    provides=" ".join(d["provides"]),
                    reason=d["reason"],
                    replaces=" ".join(d["replaces"]),
                    repository=d["repository"],
                    required_by=" ".join(d["required_by"]),
                    url=d["url"],
                    version=d["version"]
                )

            sql.session.add(model)
            try:
                sql.session.commit()
            except IntegrityError:
                sql.session.rollback()

    
    @process
    def populate_snap_tables(self):
        for pkg in self.pamac.get_all_snaps():
            try:
                d = self.pamac.get_snap_details(
                    pkg.get_name()
                )
                title = d["title"]
                if not d["icon"]:
                    d["icon"] = "/static/images/package.svg"
                sql.session.add(
                    models.Snaps(
                        pkg_format="snap",
                        app_id=d["app_id"],
                        icon=d["icon"],
                        launchable=d["launchable"],
                        title=d["title"],
                        description=d["description"],
                        download_size=d["download_size"],
                        install_date=d["install_date"],
                        installed_size=d["installed_size"],
                        installed_version=d["installed_version"],
                        license=d["license"],
                        long_description=d["long_description"],
                        name=d["name"],
                        repository=d["repository"],
                        screenshots=" ".join(d["screenshots"]),
                        url=d["url"],
                        version=d["version"],
                        channel=d["channel"],
                        channels=" ".join(d["channels"]),
                        confined=d["confined"],
                        publisher=d["publisher"]
                        )
                )
                try:
                    sql.session.commit()
                except IntegrityError:
                    sql.session.rollback()
            except KeyError:
                pass

    
    @process
    def populate_flatpak_tables(self):
        for pkg in self.pamac.get_all_flatpaks():
            d = self.pamac.get_flatpak_details(pkg)
            if d["icon"]:
                d["icon"] = d["icon"].replace(
                    "/var/lib/flatpak/appstream/flathub/x86_64/active/icons",
                    "/static/flatpak-icons"
                )
            else:
                d["icon"] = "/static/images/package.svg"
            sql.session.add(
                models.Flatpaks(
                    pkg_format="flatpak",
                    icon=d["icon"],
                    launchable=d["launchable"],
                    title=d["title"],
                    description=d["description"],
                    download_size=d["download_size"],
                    install_date=d["install_date"],
                    installed_size=d["installed_size"],
                    installed_version=d["installed_version"],
                    license=d["license"],
                    long_description=d["long_description"],
                    name=d["name"],
                    repository=d["repository"],
                    screenshots=" ".join(d["screenshots"]),
                    url=d["url"],
                    version=d["version"]
                )
            )
            try:
                sql.session.commit()
            except IntegrityError:
                sql.session.rollback()
