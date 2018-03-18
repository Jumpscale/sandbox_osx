from js9 import j

# from JumpScale9Lib.data.markdown.mistune import *

# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import HtmlFormatter

import copy

from .MarkdownDocument import *
from .MarkdownExample import *
from .MarkdownComponents import *
JSBASE = j.application.jsbase_get_class()


class MarkdownFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.markdown"
        JSBASE.__init__(self)

    def help(self, run=True):
        """
        @param execute, if execute will execute in shell & give you control to manipulate at end

        js9 'j.data.markdown.help()'

        """
        C = """

        md=j.data.document_get()

        # COMON EXAMPLES
        md.header_add(2,"this is title on level 2")

        table=md.table_add()
        table.header_add(["name","descr"])
        table.row_add(["ghent","best town ever"])
        table.row_add(["antwerp","trying to be best town ever"])

        # EXAMPLE TO ADD DATA IN MARKDOWN
        test={}
        test["descr"]="some description"
        test["nr"]=3
        test["subd"]={"nr2":3,"item":"sss"}

        md.data_add(test,"test","myguid")

        test["nr"]=4
        md.data_add(test,"test","myguid2")

        md2=self.document_get(str(md))

        print (md2.getHashList("test"))

        print(md)
        """
        j.data.text.printCode(C)
        C = j.data.text.strip(C)
        if run:
            exec(C)
            from IPython import embed
            self.logger.debug("Shell for help for markdown factory:")
            embed()

    def document_get(self, content="", path=""):
        """
        returns a tool which allows easy creation of a markdown document
        """
        return MarkdownDocument(content, path)

    def mdtable_get(self):
        return MDTable()

    def mddata_get(self):
        return MDData()


    def test(self):
        '''
        js9 'j.data.markdown.test()'
        '''

        t=self.mdtable_get()
        t.addHeader("name,description,date")
        t.addRow("aname, this is my city, 11/1/22")
        t.addRow("2, 'this is my city2', 11/3/22")
        t.addRow("1,2,3")
        t.addRow(["1","2","3"])

        r="""
        |name |description     |date   |
        |-----|----------------|-------|
        |aname|this is my city |11/1/22|
        |2    |this is my city2|11/3/22|
        |1    |2               |3      |
        |1    |2               |3      |
        """
        r=j.data.text.strip(r)
        assert str(t).strip()==r.strip()

        t2=self.document_get(r)

        table=t2.items[0]
        
        t3=self.document_get(example)

        from IPython import embed;embed(colors='Linux')

