'''
    streetleague.com XBMC Plugin
    Copyright (C) 2014 Greg Tangey

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2, cgi
import re

if sys.version_info >=  (2, 7):
    import json as _json
    from collections import OrderedDict
else:
    import simplejson as _json
    from collections_backport import OrderedDict

try:
  import StorageServer
except:
  import storageserverdummy as StorageServer


# DEBUG
dbg = False

def log(description):
  if dbg:
    xbmc.log("[ADD-ON] '%s v%s': %s" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

__addon__     = xbmcaddon.Addon()
__plugin__    = __addon__.getAddonInfo('name')
__version__   = __addon__.getAddonInfo('version')
__icon__      = __addon__.getAddonInfo('icon')
__language__  = __addon__.getLocalizedString

addonPath     = __addon__.getAddonInfo('path')

i18n = __language__

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]

cache = StorageServer.StorageServer(__plugin__, 1)

TAGS = [
  "location2015",
  "location2014",
  "location2013",
  "full",
  "athletes",
  "prelim",
  "proopenpros",
  "finals"
]

TAG_STRINGS = [
  "2015 by Location",
  "2014 by Location",
  "2013 by Location",
  "Full Videos",
  "Videos by Athlete",
  "Pro Open Pros",
  "Prelminiaries (only 2013)",
  "Finals (only 2013)"
]

USER_AGENT = ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

BASE_URL = 'http://web.mobilerider.com/clients/streetleague/api/channel/?tag='+(",".join(TAGS))
VIDEO_FILTER_URL = 'http://web.mobilerider.com/clients/streetleague/api/media/?filter='
VIDEO_DATA_URL= 'http://web.mobilerider.com/api2/2450/media/%s.json?returnUrl=http%%3A%%2F%%2Fstreetleague.com%%2Fondemand%%2F'


def add_tags(inChannels):
  i = 0;
  for name,channels in inChannels.iteritems():
    name_str = TAG_STRINGS[i]
    listitem = xbmcgui.ListItem(name_str)
    url = pluginUrl + '?mode=channels&id=' + name
    xbmcplugin.addDirectoryItem(pluginHandle, url, listitem, True, len(channels))
    i +=1

def load_remote():
  CHANNELS = OrderedDict()
  req = urllib2.Request(BASE_URL)
  req.add_header('User-Agent', USER_AGENT)
  response = urllib2.urlopen(req)
  content=response.read()
  response.close()

  jsonObj = _json.loads(content, object_pairs_hook=OrderedDict)
  objects = jsonObj['objects']
  for name,channels in objects.iteritems():
    CHANNELS[str(name)] = channels

  return CHANNELS

def load_videos(tag,inId):
  filterStr = '{"channel":{"'+tag+'":{"'+inId+'":1}},"query":""}'

  req = urllib2.Request(VIDEO_FILTER_URL+filterStr)
  req.add_header('User-Agent', USER_AGENT)
  response = urllib2.urlopen(req)
  content=response.read()
  response.close()

  jsonObj = _json.loads(content)
  videos = jsonObj['objects']

  return videos

def load_video_data(videoid):
  url = VIDEO_DATA_URL % (videoid)
  req = urllib2.Request(url)
  req.add_header('User-Agent', USER_AGENT)
  response = urllib2.urlopen(req)
  content=response.read()
  response.close()

  video_data = _json.loads(content)

  return video_data


def index():
  add_tags(cache.cacheFunction(load_remote))
  xbmcplugin.endOfDirectory(pluginHandle)

def channels(inId):
  tag_channels = cache.cacheFunction(load_remote)
  for channel in tag_channels[inId]:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', channel['name'])
    listItem = xbmcgui.ListItem(name)
    url = pluginUrl + '?mode=channel&id='+channel['id']+"&tag="+inId
    xbmcplugin.addDirectoryItem(pluginHandle,url,listItem, True)

  xbmcplugin.endOfDirectory(pluginHandle)

def channel(tag,inId):
  videos = cache.cacheFunction(load_videos,tag,inId)

  xbmc.executebuiltin("Container.SetViewMode(500)")
  for video in videos:
    title = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', video['title'])
    listItem = xbmcgui.ListItem(title, iconImage=video['thumbnail'], thumbnailImage=video['thumbnail'])
    url = pluginUrl + '?mode=play&id='+video['id']
    xbmcplugin.addDirectoryItem(pluginHandle,url,listItem, False)

  xbmcplugin.endOfDirectory(pluginHandle)

def play_video(videoid):
  data = cache.cacheFunction(load_video_data,videoid)
  video_url = data['files']['ipod']

  listitem = xbmcgui.ListItem(data['Title'], iconImage=data['thumbnails']['large'], thumbnailImage=data['thumbnails']['small'])
  infoLabels = {'title': data['Title'], 'description': data['Description']}
  listitem.setInfo('video', infoLabels)

  xbmc.Player().play(video_url, listitem)


query = cgi.parse_qs(pluginQuery[1:])
for key, value in query.items():
    query[key] = value[0]
query['mode'] = query.get('mode', '')

if query['mode'] == 'play':
  videoid = query['id']
  play_video(videoid)
elif query['mode'] == 'channels':
  inId = query['id']
  channels(inId)
elif query['mode'] == 'channel':
  tag = query['tag']
  inId = query['id']
  channel(tag,inId)
else:
  index()
