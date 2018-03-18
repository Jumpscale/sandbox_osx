from js9 import j
from .MarkdownComponents import *
JSBASE = j.application.jsbase_get_class()


class MarkdownDocument(JSBASE):

    def __init__(self, content="", path=""):
        JSBASE.__init__(self)
        if path != "":
            content = j.sal.fs.fileGetContents(path)

        self._content = content
        self._tokens = ""
        self._changed_tokens = False
        self.items = []
        self._parse()
        self._dataCache = {}

    def _findFancyHeaders(self):
        if not self.content or self.content.strip() == "":
            return
        out = []
        for line in self.content.split("\n"):
            if line.startswith("===="):
                out[-1] = "# %s" % out[-1]
                continue

            if line.startswith("-----"):
                out[-1] = "## %s" % out[-1]
                continue
            out.append(line)

        self._content = "\n".join(out)

    def table_add(self):
        """
        returns table which needs to be manipulated
        """
        t = MDTable()
        self.items.append(t)
        return t

    def header_add(self, level, title):
        """
        """
        self.items.append(MDHeader(level, title))

    def listitem_add(self, level, text):
        """
        """
        self.items.append(MDListItem(level, text))

    def comment_add(self, text):
        """
        """
        self.items.append(MDComment(text))

    def comment1line_add(self, text):
        """
        """
        self.items.append(MDComment1Line(text))

    def block_add(self, text):
        """
        """
        self.items.append(MDBlock(text))

    def code_add(self, text, lang):
        """
        """
        self.items.append(MDCode(text, lang))

    def data_add(self, ddict, name="", guid=""):
        ddict = copy.copy(ddict)
        self.items.append(MDData(ddict, name, guid))

    def _parse(self):
        self._findFancyHeaders()
        state = ""
        block = ""
        prevListLevel = 0
        curListLevel = 1
        substate = ""

        def addBlock(block):
            if block.strip() != "":
                self.block_add(block)
            substate = ""
            state = ""
            return ""

        if not self.content or self.content.strip() == '':
            return

        for line in self.content.split("\n"):

            # HEADERS
            if line.startswith("#"):
                block = addBlock(block)
                level = 0
                line0 = line
                while line0.startswith("#"):
                    level += 1
                    line0 = line0[1:]
                title = line0.strip()
                self.items.append(MDHeader(level, title))
                continue

            linestripped = line.strip()

            # substate
            if linestripped.startswith("<!--") and linestripped.endswith("-->"):
                substate = linestripped[4:-3].strip()
                self.addMDComment1Line(substate)
                block = ""
                state = ""
                continue

            if line.startswith("<!-"):
                state = "COMMENT"
                continue

            # process all comment states
            if state.startswith("COMMENT"):
                if line.startswith("-->"):
                    state = ""
                    if state == "COMMENT":
                        self.items.append(MDComment(block))
                    block = ""
                    continue
                block += "%s\n" % line

            # LIST
            if linestripped.startswith("-") or linestripped.startswith("*"):
                if state == "":
                    block = addBlock(block)
                    state = "LIST"
                    curListLevel = 1
                    prevListLevel = 0
                    prevlevels = {0: 1}

                if state == "LIST":
                    if not (linestripped.startswith("-") or linestripped.startswith("*")):
                        state
                    line0 = line
                    level = 0
                    while line0.startswith(" "):
                        level += 1
                        line0 = line0[1:]
                    # see how level goes up or down
                    if level in prevlevels:
                        curListLevel = prevlevels[level]
                    elif level > prevListLevel:
                        curListLevel += 1
                        prevlevels[level] = curListLevel
                    prevListLevel = level
                    self.items.append(MDListItem(
                        curListLevel, line.strip("* ")))
                    continue
            else:
                # get out of state state
                if state == "LIST":
                    state = ""

            if state == "TABLE" and not linestripped.startswith("|"):
                state = ""
                self.items.append(table)
                table = None
                cols = []

            # TABLE
            if state != "TABLE" and linestripped.startswith("|"):
                state = "TABLE"
                block = addBlock(block)
                cols = [item.strip()
                        for item in line.split("|") if item.strip() != ""]
                table = MDTable()
                table.addHeader(cols)
                continue

            if state == "TABLE":
                if linestripped.startswith("|") and linestripped.endswith("|") and line.find("---") != -1:
                    continue
                cols = [item.strip() for item in line.strip().strip('|').split("|")]
                table.addRow(cols)
                continue

            # CODE
            if state == "" and linestripped.startswith("```") or linestripped.startswith("'''"):
                block = addBlock(block)
                state = "CODE"
                lang = line.strip("'` ")
                continue

            if state == "CODE":
                if linestripped.startswith("```") or linestripped.startswith("'''"):
                    state = ""
                    # from pudb import set_trace; set_trace()
                    if substate.startswith("data"):
                        tmp, name, guid = substate.split("|")
                        data = j.data.serializer.yaml.loads(str(block))
                        self.data_add(data, name, guid)
                    else:
                        self.items.append(MDCode(block, lang))
                    block = ""
                else:
                    block += "%s\n" % line
                continue

            if linestripped != "":
                block += "%s\n" % line

            block = addBlock(block)

    @property
    def content(self):
        return self._content

    @property
    def tokens(self):
        if self._tokens == "":
            bl = BlockLexer()
            self._tokens = bl.parse(self._content)
        return self._tokens

    @tokens.setter
    def tokens(self, val):
        self._changed_tokens = True
        self._tokens = val

    def hashlist_get(self, ttype):
        res = {}
        for item in self.items:
            if item.type == "data" and item.name == ttype:
                res[item.guid] = item.hash
        return res

    def datacollection_get(self, ttype):
        """
        ttype is name of the data block


        """
        res = {}
        for item in self.items:
            if item.type == "data" and item.name == ttype:
                res[item.guid] = item.ddict
                key = "%s__%s" % (ttype, item.guid)
                self._dataCache[key] = item
        return res

    def dataobj_get(self, ttype, guid):
        """
        ttype is name for the block
        guid is unique id, can be name or guid or int(id)

        """
        key = "%s__%s" % (ttype, guid)
        if key not in self._dataCache:
            self.datacollection_get()
        if key not in self._dataCache:
            raise j.exceptions.Input(
                "Cannot find object with type:%s guid:%s" % (ttype, guid))
        return self._dataCache[key].ddict

    def __repr__(self):
        out = ""
        prevtype = ""
        for item in self.items:
            if item.type not in ["list"]:
                if prevtype == "list":
                    out += "\n"
                out += str(item).strip() + "\n\n"
            else:
                out += str(item).rstrip() + "\n"

            prevtype = item.type
        return out

    __str__ = __repr__

