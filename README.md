# Steam Discount Manager is a program which allows to perform custom filtering and sorting on a list of a discounted titles from Steam. This allows to focus on a really  significant / desired titles.

> :warning: **After launching the ```SteamDiscountScrapper``` or updating a database from ```SteamDiscountManager```, a browser will open**: Do not interfere, the browser will shut down itself after a minute or two.

## Features:
* Filters:
  * Discount (%): >= x
  * New price: <= x
  * Positive reviews (%): >= x
  * Number of reviews: >= x
* Sorting
* DiscountGuard

## Launch:
* First download Chromedriver. You can find it here: https://chromedriver.chromium.org/downloads IMPORTANT: Make sure that the Chromediver version corresponds with your Chrome browser version.
* Put this file in the same directory, with the rest of the files.
* Run the ```SteamDiscountManager.py``` to launch the manager.
* It is recommended to put a shortcut of the ```RUN.bat``` file into startup.

## Technology:
* ```Python``` 3.8
* ```selenium``` 3.141.0
* ```pandas``` 1.2.0
* ```tkscrolledframe``` 1.0.4

## Screenshots:
Before filtering we have ~700 titles to look on.
![sdm1](https://user-images.githubusercontent.com/71539614/109739980-bd089a80-7bca-11eb-9287-3e8b9f61cf7c.png)

After filtering there are only around 30 titles:
![sdm2](https://user-images.githubusercontent.com/71539614/109739988-bed25e00-7bca-11eb-8879-510ca57ad6c7.png)
