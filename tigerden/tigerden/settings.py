"""
Django settings for tigerden project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from oscar.defaults import *
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def location(x): return os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', x)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


if os.environ.get('DJANGO_PRODUCTION') == 'true':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    ALLOWED_HOSTS = ['192.168.26.43:80']
else:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = ')st-+2u+a=d@ky-$i8^c6196yq--axn@@==b(0g4oo-5ibck^('
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True
    ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'django.contrib.flatpages',

    'custom_apps',

    'oscar.config.Shop',
    'custom_apps.analytics.apps.AnalyticsConfig',
    'custom_apps.checkout.apps.CheckoutConfig',
    'custom_apps.address.apps.AddressConfig',
    'custom_apps.shipping.apps.ShippingConfig',
    'custom_apps.catalogue.apps.CatalogueConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.communication.apps.CommunicationConfig',
    'custom_apps.partner.apps.PartnerConfig',
    'custom_apps.basket.apps.BasketConfig',
    'oscar.apps.payment.apps.PaymentConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'custom_apps.order.apps.OrderConfig',
    'custom_apps.customer.apps.CustomerConfig',
    'oscar.apps.search.apps.SearchConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'oscar_accounts.apps.AccountsConfig',
    'oscar_accounts.dashboard.apps.AccountsDashboardConfig',
    'custom_apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'custom_apps.dashboard.users.apps.UsersDashboardConfig',
    'custom_apps.dashboard.orders.apps.OrdersDashboardConfig',
    'custom_apps.dashboard.grouporders.apps.GroupOrdersDashboardConfig',
    'custom_apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

    # 3rd-party apps that oscar depends on
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',
    'django_tables2'
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'tigerden.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [location('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.communication.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ],
            'libraries':{
                'custom_tags': 'templatetags.custom_tags'
            },
            'debug': DEBUG,
        },
    },
]

# Default primary key field type
# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

WSGI_APPLICATION = 'tigerden.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Central'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = location('tigerden/public/media')
STATIC_ROOT = location('public/static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Oscar Display Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#display-settings

OSCAR_SHOP_NAME = "Tiger Den"
OSCAR_SHOP_TAGLINE = "Where Everyone Belongs"

SUPERVISOR_EMAIL_HOST = "ecusd7"

# OSCAR_HOMEPAGE = reverse_lazy('catalogue:index')
OSCAR_HIDDEN_FEATURES = ["wishlists", "reviews"]

# DEFAULT TO 20
OSCAR_PRODUCTS_PER_PAGE = 100
# OSCAR_OFFERS_PER_PAGE
# OSCAR_REVIEWS_PER_PAGE
# OSCAR_NOTIFICATIONS_PER_PAGE
# OSCAR_EMAILS_PER_PAGE
# OSCAR_ORDERS_PER_PAGE
# OSCAR_ADDRESSES_PER_PAGE
# OSCAR_STOCK_ALERTS_PER_PAGE
OSCAR_DASHBOARD_ITEMS_PER_PAGE = 100

MAX_ONGOING_GROUP_ORDERS = 15
ONGOING_STATUS = 'Being processed'

# Oscar Order Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#order-settings

OSCAR_INITIAL_ORDER_STATUS = 'Waiting to be accepted'
OSCAR_INITIAL_LINE_STATUS = 'Waiting to be accepted'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Waiting to be accepted': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Processed': ('Cancelled',),
    'Cancelled': (),
}

OSCAR_ORDER_STATUS_CASCADE = {
    'Waiting to be accepted': 'Waiting to be accepted',
    'Being processed': 'Being processed',
    'Cancelled': 'Cancelled',
    'Processed': 'Processed'
}

OSCAR_LINE_STATUS_PIPELINE = OSCAR_ORDER_STATUS_PIPELINE

# Oscar Checkout Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#checkout-settings

OSCAR_ALLOW_ANON_CHECKOUT = True

# Oscar Review Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#review-settings

# disable it?

# Oscar Communication Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#communication-settings


OSCAR_FROM_EMAIL = "tigerdentest@gmail.com"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "tigerdentest@gmail.com"
EMAIL_HOST_PASSWORD = "rpybwftlqxlvbjrw"

# Oscar Currency Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#currency-settings

OSCAR_DEFAULT_CURRENCY = "USD"

# Oscar Media Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#upload-media-settings

OSCAR_MISSING_IMAGE_URL = MEDIA_ROOT + '/image_not_found.jpg'

# Oscar Misc Settings
# https://django-oscar.readthedocs.io/en/stable/ref/settings.html#misc-settings

# OSCAR_GOOGLE_ANALYTICS_ID

# Oscar Dashboard Structure

OSCAR_DASHBOARD_NAVIGATION = [
    {
        'label': _('Dashboard'),
        'icon': 'icon-th-list',
        'url_name': 'dashboard:index',
    },
    {
        'label': _('Catalogue'),
        'icon': 'icon-sitemap',
        'children': [
            {
                'label': _('Products'),
                'url_name': 'dashboard:catalogue-product-list',
            },
            {
                'label': _('Product Types'),
                'url_name': 'dashboard:catalogue-class-list',
            },
            {
                'label': _('Categories'),
                'url_name': 'dashboard:catalogue-category-list',
            },
            {
                'label': _('Ranges'),
                'url_name': 'dashboard:range-list',
            },
            # {
            #    'label': _('Low stock alerts'),
            #    'url_name': 'dashboard:stock-alert-list',
            # },
            {
                'label': _('Options'),
                'url_name': 'dashboard:catalogue-option-list',
            },
        ]
    },
    {
        'label': _('Fulfilment'),
        'icon': 'icon-shopping-cart',
        'children': [
            {
                'label': _('Orders'),
                'url_name': 'dashboard:order-list',
            },
            {
                'label': _('Group Orders'),
                'url_name': 'dashboard:grouporder-list',
            },
            {
                'label': _('Statistics'),
                'url_name': 'dashboard:order-stats',
            },
            {
                'label': _('Partners'),
                'url_name': 'dashboard:partner-list',
            },
            # The shipping method dashboard is disabled by default as it might
            # be confusing. Weight-based shipping methods aren't hooked into
            # the shipping repository by default (as it would make
            # customising the repository slightly more difficult).
            # {
            #     'label': _('Shipping charges'),
            #     'url_name': 'dashboard:shipping-method-list',
            # },
        ]
    },
    {
        'label': _('Customers'),
        'icon': 'icon-group',
        'children': [
            {
                'label': _('Customers'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _('Stock alert requests'),
                'url_name': 'dashboard:user-alert-list',
            },
        ]
    },
    {
        'label': 'Accounts',
        'icon': 'icon-globe',
        'children': [
            {
                'label': 'Accounts',
                'url_name': 'accounts_dashboard:accounts-list',
            },
            {
                'label': 'Transfers',
                'url_name': 'accounts_dashboard:transfers-list',
            },
            {
                'label': 'Deferred income report',
                'url_name': 'accounts_dashboard:report-deferred-income',
            },
            {
                'label': 'Profit/loss report',
                'url_name': 'accounts_dashboard:report-profit-loss',
            },
        ]
    },
    {
        'label': _('Offers'),
        'icon': 'icon-bullhorn',
        'children': [
            {
                'label': _('Offers'),
                'url_name': 'dashboard:offer-list',
            },
            {
                'label': _('Vouchers'),
                'url_name': 'dashboard:voucher-list',
            },
            {
                'label': _('Voucher Sets'),
                'url_name': 'dashboard:voucher-set-list',
            },

        ],
    },
    {
        'label': _('Content'),
        'icon': 'icon-folder-close',
        'children': [
            {
                'label': _('Pages'),
                'url_name': 'dashboard:page-list',
            },
            {
                'label': _('Email templates'),
                'url_name': 'dashboard:comms-list',
            },
            # {
            #    'label': _('Reviews'),
            #    'url_name': 'dashboard:reviews-list',
            # },
        ]
    },
    {
        'label': _('Reports'),
        'icon': 'icon-bar-chart',
        'url_name': 'dashboard:reports-index',
    },
]
