from js9 import j
JSBASE = j.application.jsbase_get_class()


class Object():
    def __init__(self):
        pass


    def __str__(self):
        out=""
        for key,val in self.__dict__.items():
            out+="%s:%s "%(key,val)
        out=out.strip()
        return out

    __repr__ = __str__


class MDTable(JSBASE):

    def __init__(self):
        self.header = []
        self.rows = []
        self.type = "table"
        JSBASE.__init__(self)

    def rows_as_objects(self):
        nrcols=len(self.header)
        res=[]
        for row in self.rows:
            oo=Object()
            for x in range(0,nrcols):
                val=row[x]
                if val.strip()==".":
                    val=""
                else:
                    try:
                        val=int(val)
                    except:
                        pass
                key=self.header[x]
                oo.__dict__[key]=val
            res.append(oo)
        return res


    def addHeader(self, cols):
        """
        cols = columns can be comma separated string or can be list
        """
        if j.data.types.string.check(cols):
            cols=[item.strip().strip("'").strip("\"").strip() for item in cols.split(",")]

        self.header = cols
        for nr in range(len(self.header)):
            if self.header[nr] is None or self.header[nr].strip() == "":
                self.header[nr] = " . "

    def addRow(self, cols):
        """
        cols = columns  can be comma separated string or can be list
        """        
        if j.data.types.string.check(cols):
            cols=[item.strip().strip("'").strip("\"").strip() for item in cols.split(",")]
        if len(cols) != len(self.header):
            raise j.exceptions.Input(
                "cols need to be same size as header. %s vs %s" % (len(cols), len(self.header)))
        for nr in range(len(cols)):
            if cols[nr] is None or str(cols[nr]).strip() == "":
                cols[nr] = " . "
        self.rows.append(cols)

    def _findSizes(self):
        m = [0 for item in self.header]
        x = 0
        for col in self.header:
            if len(col) > m[x]:
                m[x] = len(col)
            x += 1
        for row in self.rows:
            x = 0
            for col in row:
                col=str(col)
                if len(col) > m[x]:
                    m[x] = len(col)
                    if m[x]<3:
                        m[x]=3
                x += 1
        return m

    def __repr__(self):
        def pad(text, l, add=" "):
            if l<4:
                l=4
            text=str(text)
            while(len(text) < l):
                text += add
            return text
        pre = ""
        m = self._findSizes()

        # HEADER
        x = 0
        out = "|"
        for col in self.header:
            col = pad(col, m[x])
            out += "%s|" % col
            x += 1
        out += "\n"

        # INTERMEDIATE
        x = 0
        out += "|"
        for col in self.header:
            col = pad("", m[x], "-")
            out += "%s|" % col
            x += 1
        out += "\n"

        for row in self.rows:
            x = 0
            out += "|"
            for col in row:
                col = pad(col, m[x])
                out += "%s|" % col
                x += 1
            out += "\n"

        out += "\n"
        return out

    __str__ = __repr__


class MDHeader(JSBASE):

    def __init__(self, level, title):
        self.level = level
        self.title = title
        self.type = "header"
        JSBASE.__init__(self)

    def __repr__(self):
        pre = ""
        for i in range(self.level):
            pre += "#"
        return "%s %s" % (pre, self.title)

    __str__ = __repr__


class MDListItem(JSBASE):

    def __init__(self, level, text):
        self.level = level
        self.text = text
        self.type = "list"
        JSBASE.__init__(self)

    def __repr__(self):
        pre = ''
        if self.level > 1:
            pre = ' ' * (self.level - 1)
        return "%s%s" % (pre, self.text)

    __str__ = __repr__


class MDComment(JSBASE):

    def __init__(self, text):
        self.text = text
        self.type = "comment"
        JSBASE.__init__(self)

    def __repr__(self):
        out = "<!--\n%s\n-->\n" % self.text

    __str__ = __repr__


class MDComment1Line(JSBASE):

    def __init__(self, text):
        self.text = text
        self.type = "comment1line"
        JSBASE.__init__(self)

    def __repr__(self):
        out = "<!--%s-->\n" % self.text
        return out

    __str__ = __repr__


class MDBlock(JSBASE):

    def __init__(self, text):
        self.text = text
        self.type = "block"
        JSBASE.__init__(self)

    def __repr__(self):
        out = self.text
        if len(out) > 0:
            if out[-1] != "\n":
                out += "\n"
            if out[-2] != "\n":
                out += "\n"
        return out

    __str__ = __repr__


class MDCode(JSBASE):

    def __init__(self, text, lang):
        self.text = text
        self.type = "code"
        self.lang = lang
        JSBASE.__init__(self)

    def __repr__(self):
        out = self.text
        code = "\n```$lang\n$code\n```\n"
        if self.lang is None:
            self.lang = ""
        code = code.replace("$lang", self.lang)
        code = code.replace("$code", self.text)
        return code

    __str__ = __repr__


class MDData(JSBASE):

    def __init__(self, ddict, name="", guid=""):
        JSBASE.__init__(self)
        self.name = name
        self.type = "data"
        self.ddict = ddict
        self._hash = ""
        if name == "":
            if "name" in ddict:
                self.name = ddict["name"]
            else:
                raise j.exceptions.Input(
                    "name cannot be empty and could not be retrieved from dict")
        else:
            self.name = name

        if guid == "":
            if "guid" in ddict:
                self.guid = ddict["guid"]
            elif "id" in ddict:
                self.guid = ddict["id"]
            elif "name" in ddict:
                self.guid = ddict["name"]
            else:
                raise j.exceptions.Input(
                    "guid cannot be empty and could not be retrieved from dict")
        else:
            self.guid = guid


    @property
    def datahr(self):
        return j.data.serializer.yaml.dumps(self.ddict)

    @property
    def hash(self):
        if self._hash == "":
            json = j.data.serializer.json.dumps(self.ddict, True, True)
            self._hash = j.data.hash.md5_string(json)
        return self._hash

    def __repr__(self):
        out = "<!--data|%s|%s-->\n" % (self.name, self.guid)
        out += "\n"
        out += str(MDHeader(2, "%s" % self.name))
        out += "\n"
        out += str(MDCode(self.datahr, "yaml"))
        out += "\n"
        return out

    __str__ = __repr__

