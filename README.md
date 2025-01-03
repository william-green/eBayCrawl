# eBayCrawl

To setup:

- Download the source code
- Set environment variables for Telegram bot API key and channel ID. Use persistent variables.

e.g. in ~/.zshrc, create export var="value"
The application expects the variables to be "Telegram_API_KEY" and "Telegram_Channel_id"

- Restart terminal for new environment variable to take effect.
- Generate the build files

python3 setup.py sdist bdist_wheel

- Create a virtual environment to hold the project
- Run the build script

pip install dist/<wheel file>


- Run the post-install script

post_install

- Run the project

Create a script at the root level of the virtual environment.

import eBay_Crawl

eBay_Crawl.main()

Run your python script.