from jinja2 import Markup

class momentjs(object):
    def __init__(self, timestring):
        #self.timestring = timestamp.strftime("%Y-%m-%dT%H:%M:%S Z")
        self.timestring = timestring

    def render(self, format):
        #return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestring, format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")

    def utc(self):
        return self.render("utc()")
