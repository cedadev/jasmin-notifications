#!/usr/bin/env python3

import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    import jasmin_notifications.__version__ as version
except ImportError:
    # If we get an import error, find the version string manually
    version = "unknown"
    with open(os.path.join(here, "jasmin_notifications", "__init__.py")) as f:
        for line in f:
            match = re.search("__version__ *= *['\"](?P<version>.+)['\"]", line)
            if match:
                version = match.group("version")
                break

with open(os.path.join(here, "README.md")) as f:
    README = f.read()

requires = [
    "django",
    "jasmin-django-utils",
    "django-polymorphic",
    "django-picklefield",
]

if __name__ == "__main__":

    setup(
        name="jasmin-notifications",
        version=version,
        description="Django app providing flexible notifications, both as email and for rendering on site",
        long_description=README,
        classifiers=[
            "Programming Language :: Python",
            "Framework :: Django",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
        author="Matt Pryor",
        author_email="matt.pryor@stfc.ac.uk",
        url="http://www.jasmin.ac.uk",
        keywords="web django jasmin notifications email html",
        packages=find_packages(),
        zip_safe=False,
        install_requires=requires,
        tests_require=requires,
        test_suite="jasmin_notifications.test",
        package_data={
            "jasmin_notifications": ["templates/jasmin_notifications/*.html"]
        },
    )
