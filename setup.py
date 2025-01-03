from setuptools import setup, find_packages
import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
import sys

class PostInstallCommand(install):
    """Custom post-installation tasks."""
    def run(self):
        # Run the standard install process
        install.run(self)

        # Locate the SQL file and execute the script
        db_script = os.path.join(os.path.dirname(__file__), 'eBay_Crawl', 'db', 'db_init.py')
        
        #print("resolving python executable to run setup scripts.")
        #python_executable = 'python3' if sys.version_info[0] == 3 else 'python'
        
        print(f"Running post-install script: {db_script}")
        #subprocess.call([python_executable, db_script])
        subprocess.call([sys.executable, db_script])


setup(
    name='ebay_crawler',  # Name of your package
    version='0.1.0',  # Version of your package
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[  # Any dependencies your package needs
        'anyio==4.7.0',
        'appdirs==1.4.4',
        'APScheduler==3.6.3',
        'arrow==1.3.0',
        'beautifulsoup4==4.12.3',
        'binaryornot==0.4.4',
        'bs4==0.0.2',
        'cachetools==4.2.2',
        'certifi==2024.12.14',
        'chardet==5.2.0',
        'charset-normalizer==3.4.1',
        'click==8.1.8',
        'cookiecutter==2.6.0',
        'cssselect==1.2.0',
        'fake-useragent==2.0.3',
        'h11==0.14.0',
        'httpcore==1.0.7',
        'httpx==0.28.1',
        'idna==3.10',
        'importlib_metadata==8.5.0',
        'Jinja2==3.1.5',
        'lxml==5.3.0',
        'lxml_html_clean==0.4.1',
        'markdown-it-py==3.0.0',
        'MarkupSafe==3.0.2',
        'mdurl==0.1.2',
        'parse==1.20.2',
        'pyee==11.1.1',
        'Pygments==2.18.0',
        'pyppeteer==2.0.0',
        'pyquery==2.0.1',
        'python-dateutil==2.9.0.post0',
        'python-slugify==8.0.4',
        'python-telegram-bot==21.9',
        'pytz==2024.2',
        'PyYAML==6.0.2',
        'requests==2.32.3',
        'requests-html==0.10.0',
        'rich==13.9.4',
        'setuptools==75.6.0',
        'six==1.17.0',
        'sniffio==1.3.1',
        'soupsieve==2.6',
        'tenacity==9.0.0',
        'text-unidecode==1.3',
        'tornado==6.1',
        'tqdm==4.67.1',
        'types-python-dateutil==2.9.0.20241206',
        'typing_extensions==4.12.2',
        'tzlocal==5.2',
        'urllib3==1.26.20',
        'w3lib==2.2.1',
        'websockets==10.4',
        'zipp==3.21.0'
    ],
    include_package_data=True,  # To include additional files as per MANIFEST.in
    long_description=open('README.md').read(),  # Read the README for long description
    long_description_content_type='text/markdown',  # Format of the long description
    author='William Green',
    author_email='william.green@sjsu.edu',
    description='eBay crawler program',
    url='https://github.com/william-green/eBayCrawl/',  # GitHub URL or project URL
    classifiers=[  # Optional classifiers to help others find your package
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.13.1',
    entry_points={
        'console_scripts': [
            'post_install=eBay_Crawl.db.db_init:setup_db',
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)