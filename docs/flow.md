## Call Flow

Based on mobile web site HTML5 video for Streetleague.com On Demand

1. ```http://web.mobilerider.com/clients/streetleague/api/channel/?tag=full,location2014,location2013,prelim,finals,athletes,proopenpros```
2. Filter with data from step 1 - ```http://web.mobilerider.com/clients/streetleague/api/media/?filter={"channel":{"location2014":{"17520":1}},"query":""}```
3. Get video data with id from step 2 - ```http://web.mobilerider.com/api2/2450/media/77494.json?returnUrl=http%3A%2F%2Fstreetleague.com%2Fondemand%2F```
