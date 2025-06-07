'''
    Cumination
    Copyright (C) 2019 Cumination

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
import re
import xbmc
import xbmcgui
from resources.lib import utils
#from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
from resources.lib.customsite import CustomSite

site = CustomSite('Cumination', 'eroprofile')
BASE_URL = 'https://www.eroprofile.com'


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', BASE_URL + '/m/videos/home', 'Cat', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', '{0}?text='.format(BASE_URL + '/m/videos/home'), 'Search', site.img_search)
    List(BASE_URL + '/m/videos/search?niche=all-sf')
    utils.eod()
    

@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, '')
    except:
        return None
    match = re.compile(r'bg-black"><a href="([^"]+).+?<img\s*src="([^"]+).+?<div class="videoDur">([:\d]+).+?<div class="videoTtl" title="([^"]+).*?redirect-link">([^<]+)', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for videopage, img, duration, name, nice in match:
        nice = " [" + nice + "]"
        name = utils.cleantext(name + nice).title()
        site.add_download_link(name, BASE_URL + videopage, 'Playvid', img, duration=duration)
    
    nextp = re.compile('([^\"]+)\"\D*21_73').search(listhtml)
    if nextp:
        npurl = BASE_URL + nextp.group(1).replace('&amp;', '&')
        #next page number
        np = int(re.compile('(\d+)\"\D*21_73').search(listhtml).group(1))
        #current page number
        cp = int(np) - 1
        #last page number
        lp = re.compile(r'(\d+)\"\D+21_75').search(listhtml).group(1)
        nplptxt = 'Next Page (' + str(cp) + ' / ' + str(lp) + ')'
        
        cm_page = (utils.addon_sys + "?mode=custom_eroprofile_by_Cumination.GotoPage&list_mode=custom_eroprofile_by_Cumination.List&url=" + urllib_parse.quote_plus(npurl) + "&np=" + str(np) + "&lp=" + str(lp))
        cm = [('[COLOR violet]Goto Page #[/COLOR]', 'RunPlugin(' + cm_page + ')')]
        site.add_dir(nplptxt, npurl, 'List', site.img_next, contextm=cm)
    utils.eod()

@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        if lp and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        url = url.replace('pnum=' + str(np), 'pnum=' + str(pg))

        contexturl = (utils.addon_sys + "?mode=" + str(list_mode) + "&url=" + urllib_parse.quote_plus(url) + "&page=" + str(pg))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')

@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '+')
        searchUrl = searchUrl + title
        List(searchUrl)
        
@site.register()
def Cat(url):
    listhtml = utils.getHtml(url, '')
    match = re.compile(r'class="chkN marR".*?href="([^"]+)".*?class="redirect-link">([^>]+)<', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for catpage, name in match:
        name = utils.cleantext(name)
        site.add_dir(name, BASE_URL + catpage, 'List', '', '')
    utils.eod()
    
@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(18, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, '')
    videolink = re.compile(r'<source\s*src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    vp.play_from_direct_link(videolink.replace('https', 'http').replace('&amp;', '&'))