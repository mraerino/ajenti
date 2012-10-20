import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager, PermissionProvider, restrict
from reconfigure.items.ajenti import User


@plugin
class Configurator (SectionPlugin):
    def init(self):
        self.title = 'Configure'
        self.category = 'Ajenti'
        self.order = 50

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        self.find('users').new_item = lambda c: User('Unnamed', '')

        def post_user_bind(object, collection, item, ui):
            box = ui.find('permissions')
            for prov in PermissionProvider.get_all():
                line = self.ui.create('tab', title=prov.get_name())
                box.append(line)
                for perm in prov.get_permissions():
                    line.append(self.ui.create('checkbox', id=perm[0], text=perm[1], \
                        value=(perm[0] in item.permissions)))
        self.find('users').post_item_bind = post_user_bind

        def post_user_update(object, collection, item, ui):
            box = ui.find('permissions')
            for prov in PermissionProvider.get_all():
                for perm in prov.get_permissions():
                    has = box.find(perm[0]).value
                    if has and not perm[0] in item.permissions:
                        item.permissions.append(perm[0])
                    if not has and perm[0] in item.permissions:
                        item.permissions.remove(perm[0])
        self.find('users').post_item_update = post_user_update

        self.binder.autodiscover()
        self.binder.populate()

        self.find('save-button').on('click', self.save)

    @restrict('configurator:configure')
    def save(self):
        self.binder.update()
        for user in ajenti.config.tree.users.values():
            if not '|' in user.password:
                user.password = UserManager.get().hash_password(user.password)
        self.binder.populate()
        ajenti.config.save()
        self.publish()
        self.context.notify('Saved')


@plugin
class ConfigurationPermissionsProvider (PermissionProvider):
    def get_name(self):
        return 'Configuration'

    def get_permissions(self):
        return [('configurator:configure', 'Change configuration')]