import oscar.apps.dashboard.users.apps as apps


class UsersDashboardConfig(apps.UsersDashboardConfig):
    name = 'custom_apps.dashboard.users'
