import sys
sys.path.append('../')
sys.path.append('insiderScraper/')

from insiderScraper import updateTickers


def test_generateUrl():
    ticker = 'msft'
    testUrl = "http://openinsider.com/screener?s=" + ticker + \
        "&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=" +\
        "1&xs=1&xa=1&xd=1&xg=1&xf=1&xm=1&xx=1&xc=1&xw=1&vl=&vh=&ocl=&och=&s" +\
        "ic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=" +\
        "&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
    funcUrl = updateTickers.generateUrl(ticker)

    assert funcUrl == testUrl, "unable to generate download url"
