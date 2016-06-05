
import cgi
from collections import Counter

from xdfile.html import th, td, mkhref
from xdfile.metadatabase import publications, get_publication
import xdfile.utils
import xdfile

def mkcell(text, href="", title=""):
    r = '<div>'
    r += mkhref(text, href, title=title)
    r += '</div>'
    return r


def split_year(y):
    lsy = str(y)[2:]
    if y[3] != '0':
        msy = ' '  # unicode M space
    else:
        msy = str(y)[:2]

    return "%s<br/>%s" % (msy, lsy)


g_all_pubyears = None
def pubyear_html(pubyears=[]):
    global g_all_pubyears
    if not g_all_pubyears:
        g_all_pubyears = xdfile.utils.parse_tsv_data(open("pub/pubyears.tsv").read(), "pubyear")

    pubs = {}
    for pubid, year, num in g_all_pubyears:
        if pubid not in pubs:
            pubs[pubid] = Counter()
        try:
            pubs[pubid][int(year)] += int(num)
        except Exception as e:
            xdfile.utils.log(str(e))

    allyears = "1910s 1920s 1930s".split() + [ str(y) for y in range(1940, 2017) ]

    ret = '<table class="pubyears">'
    yhdr = [ '' ] + [ split_year(y) for y in allyears ]
    yhdr.append("all")

    ret += th(*yhdr, rowclass="pubyearhead")
    # Insert empty row
    ret += '<tr><td class="emptytd">&nbsp;</td></tr>' 
    
    def key_pubyears(x):
        pubid, y = x
        firstyear = xdfile.year_from_date(get_publication(pubid).row.FirstIssueDate)
        return firstyear or min(y.keys())

    xdtotal = 0
    for pubid, years in sorted(pubs.items(), key=key_pubyears):
        pubtotal = sum(years.values())
        xdtotal += pubtotal
        
        pub = publications().get(pubid)
        if pub:
            pubname = pub.row.PublicationName
            start, end = pub.row.FirstIssueDate, pub.row.LastIssueDate
        else:
            pubname, start, end = "", "", ""

        ret += '<tr>'
        ret += '<td class="pub">%s</td>' % (mkcell(pubname or pubid, "/pub/" + pubid, ))
        for y in allyears:
            classes = []

            if y[-1] == 's':
                n = sum(v for k, v in years.items() if str(k)[:-1] == y[:-2])
                y = y[:-1]
                classes.append("decade")
            else:
                n = years[int(y)]

            y = int(y)

            if (pubid, y) in pubyears:
                classes.append('this')

            if n >= 365:
                classes.append('daily')
            elif n >= 200:
                classes.append('semidaily')
            elif n >= 50:
                classes.append('weekly')
            elif n >= 12:
                classes.append('monthly')
            elif n > 0:
                pass
            elif start:
                if y < xdfile.year_from_date(start):
                    classes.append("block")
                if end and y > xdfile.year_from_date(end):
                    classes.append("block")
            else:
                classes.append("block")

            ret += '<td class="%s">%s</td>' % (" ".join(classes), mkcell(n or "", href="/pub/%s%s" % (pubid, y)))
        ret += '<td>%s</td>' % pubtotal
        ret += '</tr>'

    yhdr = yhdr[:-1]
    yhdr.append(xdtotal)
    # Insert empty row
    ret += '<tr><td class="emptytd">&nbsp;</td></tr>'    
    ret += th(*yhdr,rowclass="pubyearhead")
    ret += '</table>'
    return ret

