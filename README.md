
# PLO Ciwaruga Scrapping and Labeling

This project is created for Project class in Bandung State Polytechnics.

## Overview

The project are designed to be used in conjunction with [Label Studio](https://github.com/heartexlabs/label-studio) to create an automated system of scrapper and Label Studio itself. The app are divided into few different parts, that is :

### Scrapper

The scrapper provides the source data for the user to label. The scrapper will scrap few Indonesian news websites. The scrapper will scrap the needed information for the labeling process, which is

 - The title of the news
 - Source of the news (name of the news site)
 - Time of publicity
 - Body of the news (the article it self)

The labeling parameter it self will be described later. All of that scrapping results will not be saved by the app itself, but will be sent to the Label Studio via its API and saved there.

### Connector

The connector work is divided into 2 simple parts, Receiving and Sending. The receiving part is basically downloading the results of the labeling already done by the user in the Label Studio. And the Sending part are just sending the news that has already scrapped.

### Data Visualizer

TBA

### Labeling

The labeling part are actually not done by this app or in this app, but in Label Studio as it's already stated before. The user will label these points of the news :

 - Title click bait, is the title of the news sounds like an attempt to 
 - Misleading article, if the article has different title and article

## Usage

This part will explain how to use the API-like interface with the app, and explain the intended outcome of the app.

NOTE :
If your auth file is still empty, any attempt of authentication will be allowed as an admin. 

### update

The update function are intended to updates Label Studio via it's API system of new Scrapped news. Once a request is received the scrapper instance will be started, and will send its scrap result into Label Studio.

|Type|Value|
|--|--|
|Link|/update|
|Request Type|POST/GET|
|Auth Type|Admin Only|

***Query Variables***
|Variable name|Type|Explanation|
|--|--|--|
|kompas|integer|The amount of news to be scraped from kompas|
|detik|integer|The amount of news to be scraped from detik|
|republika|integer|The amount of news to be scraped from republika|

All the variables are optional. Pass the variables via GET method only.

***Response***
|Code|Body|
|--|--|
|200|Success|
|400|Error|


### set labelurl

This function of the API will updates the Label Studio URL within the currently running app and the configuration file itself.

|Type|Value|
|--|--|
|Link|/set/labelurl|
|Request Type|POST|
|Auth Type|Admin Only|

***Query Variables***
|Variable name|Type|Explanation|
|--|--|--|
|url|string|The url of the main page of Label Studio, cannot be empty or have length of zero|

All of the variables are cannot have length of zero. All of the variables are required.

***Response***
|Code|Body|
|--|--|
|200|Success|
|400|Error|

### add user

This function of the API will adds user into the auth file within the app.

|Type|Value|
|--|--|
|Link|/add/user	|
|Request Type|POST|
|Auth Type|Admin Only|

***Query Variables***
|Variable name|Type|Explanation|
|--|--|--|
|username|string|The username of the user, cannot be a duplicate of other user|
|password|string|The password of the user|
|role|string|The role of the user, the only valid input are `user` or `admin`|

All of the variables are cannot have length of zero. All of the variables are required.

***Response***
|Code|Body|
|--|--|
|200|Success|
|400|Duplicate|
|400|Error|

### get list

Get the list of already saved file containing the labeling result by the user in the Label Studio. All of the files listed are in the result folder specified by the parameters file.

|Type|Value|
|--|--|
|Link|/get/list|
|Request Type|POST|
|Auth Type|Admin/User|

***Response***
|Code|Body|
|--|--|
|200|JSON List of file|

Example of the JSON response :
`[ "results-26052020-174501.json", "results-25052020-154501.json"]`

### get content

Get the content of the file listed by get list. The file is guaranteed to be JSON.

|Type|Value|
|--|--|
|Link|/get/content|
|Request Type|POST|
|Auth Type|Admin/User|

***Query Variables***
|Variable name|Type|Explanation|
|--|--|--|
|filename|string|The name of the file, including `.json`|

All of the variables are cannot have length of zero. All of the variables are required.

***Response***
|Code|Body|
|--|--|
|200|content of file in JSON|
|404|Not Found|

JSON file follows the JSON_MIN format of Label Studio

### get update

Upon requesting this, the app will download the labeling result from the specified Label Studio URL. The saved file name will be the response of the program.

|Type|Value|
|--|--|
|Link|/get/update|
|Request Type|POST|
|Auth Type|Admin/User|

***Response***
|Code|Body|
|--|--|
|200|filename in JSON|

Example of the JSON
`"results-26052020-174501.json"`

## Configuration

TBA
