#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2011-2012 Martin Beran (info@berycz.net)
# license MIT/X11 (read more in the file LICENSE)

# Homepage: http://www.pywlibs.net/
# Source code: https://github.com/berycz/pywlibs
# Documentation: http://www.pywlibs.net/docs/xhtml

#VERSION 1.0

# Supported doctypes:
#  'XHTML 1.0 Transitional'   (default)
#  'XHTML 1.0 Strict'
#  'XHTML 1.0 Frameset'
#  'XHTML 1.1'
#  'HTML 4.01 Transitional'
#  'HTML 4.01 Strict'
#  'HTML 4.01 Frameset'

#TODO:
# in version 2.0
# - HTML5
# maybe in the future
# - Element:
#   - editable (edit/rm/pop etc)
#   - attributes - edit exists with attr(), delete rmAttr()


from xml.sax.saxutils import escape

_MINIMIZE = False

class Base:
  """
  main class for generating (X)HTML
  """
  _attr_entities = {'"': "&quot;", '\n': '&#10;', '\r': '&#13;', '\t':'&#9;'}

  def __init__(self, doctype='XHTML 1.0 Transitional', min=False):
    """
    constructor

    @type doctype: basestring
    @param doctype: version of the markup language
    @type min: bool
    @param min: minimizes the code - no comments, no new lines '\n' around tags
    """
    global _MINIMIZE

    self._doctype = doctype
    if self._doctype.startswith('X'):
      self.unpaired_mask = '<%s%s />'
    else:
      self.unpaired_mask = '<%s%s>'

    if min:
      _MINIMIZE = True
    else:
      _MINIMIZE = False

    # in class Element() we use methods self.attr() and self.attrs()
    # for something else than here, se we have to specify this
    self._gen_attr = self.attr
    self._gen_attrs = self.attrs

  def __repr__(self):
    return "%s()" % self.__class__.__name__

  def __str__(self):
    return "<%s generator>" % self.__class__.__name__.upper()

  def attr(self, name, value):
    """
    generates an attribute

    @type name: str
    @param name: name of attribute
    @type value: basestring
    @param value: value of attribute
    @rtype: basestring
    @return: an attribute
    """
    if name == 'class' and isinstance(value, (tuple, list)):
      v = ' '.join(value)
    else:
      v = escape('%s' % value, self._attr_entities)
    return '%s="%s"' % (name.lower(), v)

  def attrs(self, data, start=''):
    """
    generates a string of attributes

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: attributes
    @type start: str
    @param start: set ' ' if you need the returned string with space on the beginning
    @rtype: basestring
    @return: string of attributes
    """
    a = ''

    if isinstance(data, basestring):
      a = data
    elif isinstance(data, (list, tuple)):
      r = []
      for i in data:
        if not i: continue
        if isinstance(i, basestring):
          r.append(i)
        else:  # list/tuple
          if len(i) == 1:
            r.append(self._gen_attr(i[0], i[0]))  # checked, selected, multiple etc
          else:
            r.append(self._gen_attr(i[0], i[1]))
      a = ' '.join(r)
    else:  # dict/OrderedDict
      a = ' '.join([self._gen_attr(k, data[k]) for k in data])

    if a and a.startswith(start):
      return a
    elif a:
      return '%s%s' % (start, a)
    else:
      return ''

  def starttag(self, name, attrs=[], paired=True):
    """
    generates start-tag of an element

    @type name: str
    @param name: name of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type paired: bool
    @param paired: True - <tag></tag> | False - <tag />
    @rtype: basestring
    @return: XHTML element
    """
    n = name.lower()
    a = self._gen_attrs(attrs, ' ')
    if paired:
      return '<%s%s>' % (n, a)
    else:
      return self.unpaired_mask % (n, a)

  def endtag(self, name, comment=None, paired=True):
    """
    generates start-tag of an element

    @type name: str
    @param name: name of element
    @type comment: basestring|None
    @param comment: <!-- /something --> behind the tag
    @type paired: bool
    @param paired: True - <tag></tag> | False - <tag />
    @rtype: basestring
    @return: XHTML element
    """
    n = name.lower()
    if comment is None:
      c = ''
    else:
      if comment.startswith('/'):
        c = self.comment(comment)
      else:
        c = self.comment('/%s' % comment)
    if paired:
      return '</%s>%s' % (n, c)
    else:
      return c

  def element(self, name, attrs=[], content=None, comment=None, sep='', paired=True):
    """
    generates a XHTML element

    @type name: str
    @param name: name of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type content: None|basestring
    @param content: content of the element
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @type sep: basestring
    @param sep: separator, use '\n' if you want to 'separate' lines
    @type paired: bool
    @param paired: True - <tag></tag> | False - <tag />
    @rtype: basestring
    @return: XHTML element
    """
    if _MINIMIZE:
      sep = ''
    if paired:
      if content:
        c = '%s%s%s' % (sep, content, sep)
      else:
        c = ''
      return '%s%s%s' % (self.starttag(name, attrs), c, self.endtag(name, comment))
    else:
      if comment is not None:
        cm = self.comment(comment)
      else:
        cm = ''
      return '%s%s' % (self.starttag(name, attrs), cm)

  def comment(self, text=''):
    """
    returns a xhtml comment

    @type text: basestring
    @param text: description
    @rtype: basestring
    @return: XHTML element
    """
    if _MINIMIZE:
      return ''
    if text:
      t = ' %s ' % text
    else:
      t = ' '
    return '<!--%s-->' % t


class FastXhtml(Base):
  """
  generates (X)HTML elements - fast rendering
  """

  def __init__(self, doctype='XHTML 1.0 Transitional', min=False):
    """
    constructor

    @type doctype: basestring
    @param doctype: version of the markup language
    @type min: bool
    @param min: minimizes the code - no comments, no new lines '\n' around tags
    """
    Base.__init__(self, doctype, min)

    self._called_method = None

    self._unpaired = (  # <tag />
      'area', 'base', 'basefont', 'br', 'col', 'frame', 'hr', 'img', 'input',
      'link', 'meta', 'param'
    )

    self._separated_elements = (  # <tag>\ncontent\n</tag>
      'address', 'applet', 'blockquote', 'body', 'center', 'code', 'dir', 'div',
      'dl', 'fieldset', 'form', 'frameset', 'head', 'html', 'iframe', 'ol',
      'optgroup', 'map', 'menu', 'pre', 'select', 'script', 'style',
      'table', 'thead', 'tbody', 'tfoot', 'tr', 'ul',
    )

  def __getattr__(self, name):
    self._called_method = name

    multi_input = {
      'texts': 'text',
      'hiddens': 'hidden',
      'checkboxes': 'checkbox',
      'radios': 'radio',
      'submits': 'submit',
      'resets': 'reset',
      'passwords': 'password',
      'files': 'file'
    }

    if name in ('ul', 'ol', 'dir', 'menu'):
      return self._list

    elif name in ('text', 'hidden', 'checkbox', 'radio', 'submit', 'reset', 'password', 'file'):
      return self._input

    elif name in multi_input:
      self._called_method = multi_input.get(self._called_method, self._called_method)
      return self._inputs

    elif name in self._unpaired:
      return self._unpaired_element

    else:
      return self._paired_element

  def _unpaired_element(self, attrs=[], comment=None):
    """
    generates empty elements (br, hr, ...)

    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    name = self._called_method
    a = self.attrs(attrs, ' ')
    return self.element(name, a, comment=comment)

  def _paired_element(self, content='', attrs=[], comment=None, sep=None):
    """
    generates non-empty elements (div, span, p, ...)

    @type content: None|basestring
    @param content: content of the element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @type sep: str|None
    @param sep: separator - more lines or just one
    @rtype: basestring
    @return: XHTML element
    """
    name = self._called_method
    a = self.attrs(attrs, ' ')
    return self.element(name, a, content, comment, sep=sep)

  def _list(self, data, attrs=[], comment=None, sep='\n'):
    """
    generates a list ul/ol
    examples of options:
      - '<il value="smth">Something</il>\n...'
      - list of basestrings - ['1', '2', '3', '4', ...]
      - list/tuple - [[text, attr1, attr2, ...], ...]
      - dict/OrderedDict - {text: [attr1, attr2, ...]}

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: list items
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @type sep: str
    @param sep: separator - default new line
    @rtype: basestring
    @return: XHTML element
    """
    name = self._called_method

    l = ''

    if isinstance(data, basestring):
      l = data
    elif isinstance(data, (list, tuple)):
      r = []
      for i in data:
        if isinstance(i, (list, tuple)):
          t = i[0]
          a = []
          if len(i) > 1:
            a = i[1:]
          r.append(self.li(t, a))
        else:  # basestring/int/float etc
          r.append(self.li('%s' % i))
      l = sep.join(r)
    else:  # dict/OrderedDict
      l = sep.join([self.li(k, data[k]) for k in data])

    return self.element(name, attrs, l, comment, sep=sep)

  def _input(self, name, value='', attrs=[], comment=None):
    """
    generates a text/hidden/checkbox/radio input

    @type name: str
    @param name: name of field
    @type value: basestring
    @param value: default value of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element - field
    """
    element_type = self._called_method
    a = self.attrs(attrs, ' ')
    attrs2 = [('type', element_type), ('name', name)]
    if element_type != 'file':
      attrs2.append(('value', value))
    a2 = self.attrs(attrs2, ' ')
    return self.element('input', '%s%s' % (a2, a), comment=comment)

  def _inputs(self, name, options=[], checked=[], labels=None, attrs=[]):
    """
    generates list of inputs
    examples of options:
      - list/tuple - [value_and_text_of_label, ...]
      - list/tuple - [[value, label], ...]
      - list/tuple - [[value, label, attr1, attr2, ...], ...]
      - dict/OrderedDict - {value: label, ...}
      - dict/OrderedDict - {value: [label, attr1, attr2, ...], ...}
    returns 'the same' type as var options has (list/dict)

    @type name: str
    @param name: name of field
    @type options: list|tuple|dict|OrderedDict
    @param options: options of the inputs
    @type checked: basestring|list|tuple
    @param checked: checked values of field (only radios and checkboxes)
    @type labels: bool|None
    @param labels: if True - returns inputs in label
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @rtype: list|dict
    @return: list|dict of XHTML elements - fields ()
    """
    if labels is None:
      if self._called_method in ('hidden', 'submit', 'reset'):
        labels = False
      else:
        labels = True
    if self._called_method in ('checkbox', 'radio'):
      label_mask = '%(input)s %(text)s'
    else:
      label_mask = '%(text)s: %(input)s'

    if checked and self._called_method not in ('radio', 'checkbox'):
      checked = []

    if isinstance(checked, basestring):
      checked = [checked]

    if isinstance(options, (list, tuple)):
      r = []
      for i in options:
        if isinstance(i, basestring):
          ch = ([], ['checked'])[i in checked]
          input = self._input(name, i, ch)
          if labels:
            r.append(self.label(label_mask % {'input': input, 'text': i}))
          else:
            r.append(input)
        else:  # list/tuple
          t = None
          a = ''
          if len(i) > 1:
            t = i[1]
          if len(i) > 2:
            a = self.attrs(i[2:], ' ')
          a2 = self.attrs([([], ['checked'])[i[0] in checked]], ' ')
          input = self._input(name, i[0], '%s%s' % (a2, a))
          if labels:
            r.append(self.label(label_mask % {'input': input, 'text': t}))
          else:
            r.append(input)
    else:  # dict/OrderedDict
      r = {}
      for k in options:
        if isinstance(options[k], (tuple, list)):
          a = self.attrs(options[k][1:], ' ')
          a2 = self.attrs([([], ['checked'])[k in checked]], ' ')
          input = self._input(name, k, '%s%s' % (a2, a))
          if labels:
            r[k] = self.label(label_mask % {'input': input, 'text': options[k][0]})
          else:
            r[k] = input
        elif isinstance(options[k], basestring):
          ch = ([], ['checked'])[k in checked]
          input = self._input(name, k, ch)
          if labels:
            r[k] = self.label(label_mask % {'input': input, 'text': options[k]})
          else:
            r[k] = input

    return r

  def __table_content(self, data):
    """
    generates content of table, thead, tbody, tfoot, tr, th, td

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @rtype: basestring
    @return: XHTML element
    """
    if _MINIMIZE:
      sep = ''
    else:
      sep = '\n'
    _methods = {
      'thead': self.thead,
      'tfoot': self.tfoot,
      'tbody': self.tbody,
      'tr': self.tr,
      'th': self.th,
      'td': self.td
    }
    c = ''
    if not data:
      pass
    elif isinstance(data, basestring):
      c = data
    elif isinstance(data, (list, tuple)):
      cl = []
      for i in data:
        # i = dict/OrderedDict
        if i['tag'] in _methods:
          cl.append(_methods[i['tag']](i.get('data', []), i.get('attrs', [])))
      c = sep.join(cl)
    else:  # dict/OrderedDict
      cl = []
      for tag in data:
        for i in data[tag]:
          # i = dict/OrderedDict
          if tag in _methods:
            cl.append(_methods[tag](i.get('data', []), i.get('attrs', [])))
      c = sep.join(cl)
    return c

  def starttag(self, name, attrs=[]):
    """
    generates start-tag of an element

    @type name: str
    @param name: name of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @rtype: basestring
    @return: XHTML element
    """
    paired = (name.lower() not in self._unpaired)
    return Base.starttag(self, name, attrs, paired)

  def endtag(self, name, comment=None):
    """
    generates start-tag of an element

    @type name: str
    @param name: name of element
    @type comment: basestring|None
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    paired = (name.lower() not in self._unpaired)
    return Base.endtag(self, name, comment, paired)

  def element(self, name, attrs=[], content=None, comment=None, sep=None):
    """
    generates a XHTML element

    @type name: str
    @param name: name of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type content: None|basestring
    @param content: content of the element
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @type sep: basestring|None
    @param sep: separator, use '\n' if you want to 'separate' lines
    @rtype: basestring
    @return: XHTML element
    """
    paired = (name.lower() not in self._unpaired)
    if sep is None and name in self._separated_elements:
      s = '\n'
    elif sep is None:
      s = ''
    else:
      s = sep
    return Base.element(self, name, attrs, content, comment, s, paired)

  def doctype(self):
    """
    returns a doctype element

    @rtype: basestring
    @return: XHTML element
    """

    if self._doctype == 'HTML 4.01 Transitional':
      r = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" '
      r += '"http://www.w3.org/TR/html4/loose.dtd">'
    elif self._doctype == 'HTML 4.01 Strict':
      r = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
      r += '"http://www.w3.org/TR/html4/strict.dtd">'
    elif self._doctype == 'HTML 4.01 Frameset':
      r = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" '
      r += '"http://www.w3.org/TR/html4/frameset.dtd">'
    elif self._doctype == 'XHTML 1.0 Strict':
      r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
      r += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
    elif self._doctype == 'XHTML 1.0 Frameset':
      r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" '
      r += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">'
    elif self._doctype == 'XHTML 1.1':
      r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
      r += '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
    else:  # default 'XHTML 1.0 Transitional'
      r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
      r += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
    return r

  def a(self, content, href=None, name=None, title=None, target=None, lang=None, attrs=[], comment=None):
    """
    generates an anchor

    @type content: basestring|None
    @param content: content/text of the anchor (content of the element)
    @type href: basestring|None
    @param href: the destination of a link
    @type name: basestring|None
    @param name: the name of the anchor
    @type title: basestring|None
    @param title: extra information about the anchor
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    attrs2 = []
    if href is not None:
      attrs2.append(('href', href))
    elif name is not None:
      attrs2.append(('name', name))
    couples = (('title', title), ('target', target), ('hreflang', lang))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('a', '%s%s' % (a2, a), content, comment=comment)

  def img(self, src, alt, width=None, height=None, title=None, attrs=[], comment=None):
    """
    generates an image

    @type src: basestring
    @param src: source (url) of the image
    @type alt: basestring
    @param alt: alternate text for the image
    @type width: basestring|None
    @param width: width of the image
    @type height: basestring|None
    @param height: height of the image
    @type title: basestring|None
    @param title: extra information about the image
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    attrs2 = [('src', src), ('alt', alt)]
    if title is None:
      title = alt
    couples = (('title', title), ('width', width), ('height', height))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('img', '%s%s' % (a2, a), comment=comment)

  def form(self, content, action, method=None, enctype=None, attrs=[], comment=None):
    """
    generates form element

    @type content: basestring
    @param content: content of the element (description or with field)
    @type action: basestring
    @param action: where to send the form-data when the form is submitted
    @type method: basestring|None
    @param method: how to send form-data
    @type enctype: basestring|None
    @param enctype: how form-data should be encoded before sending it to a server
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    if content:
      c = content
    else:
      c = ''
    a = self.attrs(attrs, ' ')
    attrs2 = [('action', action)]
    couples = (('method', method), ('enctype', enctype))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('form', '%s%s' % (a2, a), c, comment)

  def label(self, content, for_id=None, attrs=[], comment=None):
    """
    generates a label

    @type content: None|basestring
    @param content: content of the element (description, can be with field)
    @type for_id: str
    @param for_id: id of a field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    if for_id:
      a2 = self.attrs([('for', for_id)], ' ')
    else:
      a2 = ''
    return self.element('label', '%s%s' % (a2, a), content, comment=comment)

  def fieldset(self, content, label=None, attrs=[], comment=None):
    """
    generates a fieldset

    @type content: None|basestring
    @param content: content of the element
    @type label: None|basestring
    @param label: content of label
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    if label is None:
      c = content
    else:
      c = '%s\n%s' % (self.label(label), content)
    if comment is None:
      cm = label
    else:
      cm = comment
    return self.element('fieldset', a, c, cm)

  def textarea(self, name, content='', cols=20, rows=4, attrs=[], comment=None):
    """
    generates textarea

    @type name: str
    @param name: name of field
    @type content: basestring
    @param content: default value of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element - field
    """
    a = self.attrs(attrs, ' ')
    a2 = self.attrs([('name', name), ('cols', cols), ('rows', rows)], ' ')
    return self.element('textarea', '%s%s' % (a2, a), content, comment=comment)

  def button(self, type, content='', name=None, value=None, attrs=[], comment=None):
    """
    generates a button

    @type type: str
    @param type: type of button - button, reset, submit
    @type content: basestring
    @param content: description (content of the element)
    @type name: str
    @param name: name of field
    @type value: basestring
    @param value: default value of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element - field
    """
    a = self.attrs(attrs, ' ')
    attrs2 = [('type', type)]
    couples = (('name', name), ('value', value))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('button', '%s%s' % (a2, a), content, comment=comment)

  def style(self, content, media=None, type='text/css', comment=None):
    """
    generates a style element

    @type content: basestring
    @param content: css definitions (content of the element)
    @type media: str
    @param media: styles for different media types
    @type type: str
    @param type: type of style, the only possible value is "text/css"
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    attrs2 = [('type', type)]
    couples = (('media', media), )
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('style', a2, content, comment=comment)

  def script(self, content=None, src=None, type='text/javascript', charset=None, attrs=[], comment=None):
    """
    generates a script element

    @type content: basestring|None
    @param content: script definitions (content of the element)
    @type src: basestring|None
    @param src: source (url) of the script
    @type type: str|None
    @param type: the MIME type of a script
    @type charset: str|None
    @param charset: the character encoding used in an external script file
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    attrs2 = [('type', type)]
    couples = (('src', src), ('charset', charset))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    if content is not None:
      if _MINIMIZE or self._doctype.startswith('X'):
        c = content
      else:
        c = '/* <![CDATA[ */\n%s\n/* ]]> */' % content
      return self.element('script', '%s%s' % (a2, a), c, comment=comment)
    else:
      return self.element('script', '%s%s' % (a2, a), self.comment(), comment=comment, sep='')

  def link(self, rel=None, href=None, type=None, attrs=[], comment=None):
    """
    generates link

    @type rel: None|basestring
    @param rel: the relationship between the current document and the linked document
    @type href: None|basestring
    @param href: the location of the linked document
    @type type: None|basestring
    @param type: the MIME type of the linked document
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: next attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    attrs2 = []
    couples = (('rel', rel), ('type', type), ('href', href))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('link', '%s%s' % (a, a2), comment=comment)

  def meta(self, content, name=None, http_equiv=None, attrs=[], comment=None):
    """
    generates meta tag

    @type content: basestring
    @param content: the content of the meta information
    @type name: None|basestring
    @param name: a name for the information in the content attribute
    @type http_equiv: None|basestring
    @param http_equiv: an HTTP header for the information in the content attribute
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: next attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    a = self.attrs(attrs, ' ')
    attrs2 = [('content', content)]
    couples = (('name', name), ('http-equiv', http_equiv))
    attrs2.extend([(i[0], i[1]) for i in couples if i[1] is not None])
    a2 = self.attrs(attrs2, ' ')
    return self.element('meta', '%s%s' % (a, a2), comment=comment)

  def table(self, data=[], attrs=[], comment=None):
    """
    generates a table
    example of data in Element.__init__

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    c = self.__table_content(data)
    return self.element('table', attrs, c, comment)

  def thead(self, data=[], attrs=[], comment=None):
    """
    generates a table header
    example of data in Element.__init__

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    c = self.__table_content(data)
    return self.element('thead', attrs, c, comment)

  def tbody(self, data=[], attrs=[], comment=None):
    """
    generates a table body
    example of data in Element.__init__

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    c = self.__table_content(data)
    return self.element('tbody', attrs, c, comment)

  def tfoot(self, data=[], attrs=[], comment=None):
    """
    generates a table footer
    example of data in Element.__init__

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    c = self.__table_content(data)
    return self.element('tfoot', attrs, c, comment)

  def tr(self, data=[], attrs=[], comment=None):
    """
    generates a table row
    example of data in Element.__init__

    @type data: basestring|list|tuple|dict|OrderedDict
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    c = self.__table_content(data)
    return self.element('tr', attrs, c, comment)

  def td(self, data='', attrs=[], comment=None):
    """
    generates a table cell
    example of data in Element.__init__

    @type data: basestring
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    return self.element('td', attrs, data, comment)

  def th(self, data='', attrs=[], comment=None):
    """
    generates a table header cell
    example of data in Element.__init__

    @type data: basestring
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element
    """
    return self.element('th', attrs, data, comment)

  def select(self, name, options=[], selected=[], attrs=[], comment=None):
    """
    generates a select
    if you want multiple select, set attrs=[['multiple']]
    examples of options:
      - '<option value="smth">Something</option>\n...'
      - list/tuple - [[value, text], ...]
      - list/tuple - [[value, text, attr1, attr2, ...], ...]
      - dict/OrderedDict - {value: text, ...}
      - dict/OrderedDict - {value: [text, attr1, attr2, ...], ...}
    if you want select with optgroups, you have to generate the string-options

    @type name: str
    @param name: name of field
    @type options: basestring|list|tuple|dict|OrderedDict
    @param options: options of the select
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML element - field
    """
    a = self.attrs(attrs, ' ')
    a2 = self.attrs([('name', name)], ' ')
    o = self._options(options, selected)
    return self.element('select', '%s%s' % (a2, a), o, comment=comment)

  def optgroup(self, label, options, selected=[], attrs=[], comment=None):
    """
    generates a group of options for select

    @type label: basestring
    @param label: title of optgroup
    @type options: basestring|list|tuple|dict|OrderedDict
    @param options: options of the group
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: XHTML code of the optgroup
    """
    a = self.attrs(attrs, ' ')
    a2 = self.attrs([('label', label)], ' ')
    o = self._options(options, selected)
    return self.element('optgroup', '%s%s' % (a2, a), o, comment=comment)

  def option(self, value, content=None, selected=False, attrs=[], comment=None):
    """
    generates an option for select

    @type value: basestring
    @param value: value of attribute
    @type content: basestring|None
    @param content: content of the option (content of the element), if None content=value
    @type selected: bool|int
    @param selected: True/False/1/0
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: basestring
    @return: an attribute
    """
    t = (content, value)[content is None]
    a = self.attrs(attrs, ' ')
    attrs2 = [('value', value)]
    if selected:
      attrs2.append(('selected',))
    a2 = self.attrs(attrs2, ' ')
    return self.element('option', '%s%s' % (a2, a), t, comment=comment)

  def _options(self, data, selected=[], sep='\n'):
    """
    generates a string of more options for select

    @type data: list|tuple
    @param data: attributes
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type sep: str
    @param sep: separator - default new line
    @rtype: basestring
    @return: string of attributes
    """
    if _MINIMIZE:
      sep = ''
    o = ''
    sel = selected
    if not isinstance(sel, (list, tuple)):
      sel = [sel]

    r = []
    for i in data:
      if isinstance(i, (list, tuple)):
        v = i[0]
        if len(i) == 1:
          t = i[0]
        else:
          t = i[1]
        a = i[2:]
      else:  # basestring/int/float
        v = i
        t = None
        a = []
      s = (v in sel)
      r.append(self.option(v, t, s, a))
    o = sep.join(r)

    return o


class Xhtml(FastXhtml):
  """
  generates (X)HTML elements - more comfortable, but slower
  """

  def table(self, data=[], attrs=[], comment=None):
    a = Table(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def thead(self, data=[], attrs=[], comment=None):
    a = THead(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def tbody(self, data=[], attrs=[], comment=None):
    a = TBody(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def tfoot(self, data=[], attrs=[], comment=None):
    a = TFoot(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def tr(self, data=[], attrs=[], comment=None):
    a = TRow(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def td(self, data='', attrs=[], comment=None):
    a = TCell(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def th(self, data='', attrs=[], comment=None):
    a = THCell(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def select(self, name, options=[], selected=[], attrs=[], comment=None):
    a = Select(name, options, selected, attrs, comment)
    a._doctype = self._doctype
    return a

  def optgroup(self, label, options=[], selected=[], attrs=[], comment=None):
    a = Optgroup(label, options, selected, attrs, comment)
    a._doctype = self._doctype
    return a

  def option(self, value, content=None, selected=False, attrs=[], comment=None):
    a = Option(value, content, selected, attrs, comment)
    a._doctype = self._doctype
    return a

  def _options(self):
    "is not needed"
    pass

  def ul(self, data=[], attrs=[], comment=None):
    a = Ul(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def ol(self, data=[], attrs=[], comment=None):
    a = Ol(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def dir(self, data=[], attrs=[], comment=None):
    a = Dir(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def menu(self, data=[], attrs=[], comment=None):
    a = Menu(data, attrs, comment)
    a._doctype = self._doctype
    return a

  def li(self, data=[], attrs=[], comment=None):
    a = Li(data, attrs, comment)
    a._doctype = self._doctype
    return a


class Element(Base):
  """
  generates element
  just main class, you cannot use it
  """
  # separator for Base.element()
  _separator = '\n'

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = []

  # the highest (root) element
  _root = 'html'

  ## lists of data
  _lists = {}

  ## classes of elements
  _elements = {}

  def __init__(self, data=[], attrs=[], comment=None):
    """
    constructor
    examples of data:
      1) list/tuple of dicts/OrderedDicts
      data = [
        {
          'tag': 'thead',
          'data': [
            {
              'tag': 'tr',
              'data': [
                {
                  'tag': 'td',
                  'data': 'cell-1',
                  'attrs': (('class', 'odd'),)
                },
                {
                  'tag': 'td',
                  'data': 'cell-2',
                  'attrs': (('class', 'even'),)
                },
              ]
            }
          ]
        }
      ]

      2) dict/OrderedDict of lists/tuples
      data = {
        'thead': [
          {
            'data': {
              'tr': [
                {
                  'data': {
                    'td': [
                      {
                        'data': 'cell-1',
                        'attrs': (('class', 'odd'),)
                      },
                      {
                        'data': 'cell-2',
                        'attrs': (('class', 'even'),)
                      },
                    ]
                  }
                },
              ]
            }
          }
        ]
      }

    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    # in this class we use methods self.attr() and self.attrs()
    # for something else than here, se we have to specify this
    self._gen_attr = self._attr
    self._gen_attrs = self._attrs

    self._attrs_data = []
    self._called_method = None
    self._content = ''
    if attrs: self.attrs(attrs)
    self._comment = comment
    self.extend(data)

  def __getattr__(self, name):
    n = name.lower()
    if n not in self._allowed:
      raise AttributeError("%s is not allowed element name" % name)
    self._called_method = n
    return self._append

  def __str__(self):
    """
    !!! returns your string, can be unicode !!!
    """
    return self.__unicode__()

  def __unicode__(self):
    return self.render()

  def _attr(self, name, value):
    """
    method attr() is overloaded for appending attributes
    """
    return Base.attr(self, name, value)

  def _attrs(self, data, start=''):
    """
    method attrs() is overloaded for extending attributes
    """
    return Base.attrs(self, data, start)

  def attr(self, *args):
    """
    just appends an attribute to the element or returns generated attributes

    @type args: list
    @param args: name[, value]
    @rtype: basestring|Element
    @return: if no args, returns generated attributes, else returns self
    """
    if not args:
      return self._attrs(self._attrs_data)
    elif len(args) == 1:
      self._attrs_data.append(args[0])
    else:  # len(args) > 1
      self._attrs_data.append((args[0], args[1]))
    return self

  def attrs(self, data=None):
    """
    just extends attributes of the element or returns generated attributes

    @type data: None|basestring|list|tuple|dict|OrderedDict
    @param data: attributes
    @rtype: basestring|Element
    @return: if data=None, returns generated attributes, else returns self
    """
    if data is None:
      return self._attrs(self._attrs_data)
    elif isinstance(data, basestring):
      self._attrs_data.extend([data])
    elif isinstance(data, (list, tuple)):
      self._attrs_data.extend(data)
    else:  # dict/OrderedDict
      for k in data:
        self._attrs_data.append((k, data[k]))
    return self

  def _append(self, data=[], attrs=[]):
    """
    appends element
  
    @type element: basestring
    @param element: element / tag
    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @rtype: Element|None
    @return: instance of an element-class or None for an unexpected element
    """
    l = self._lists.get(self._called_method)
    c = self._elements.get(self._called_method)
    l.append(c(data, attrs))
    return l[-1]

  def extend(self, data):
    """
    extend element of data
  
    @type data: basestring|list|tuple
    @param data: data of element
    """
    if not data:
      pass
    elif isinstance(data, basestring):
      self._content = data
    elif isinstance(data, (list, tuple)):
      for i in data:
        # i = dict/OrderedDict
        self._called_method = i['tag']
        self._append(i.get('data', []), i.get('attrs', []))
    else:  # dict/OrderedDict
      for tag in data:
        for i in data[tag]:
          # i = dict/OrderedDict
          self._called_method = tag
          self._append(i.get('data', []), i.get('attrs', []))

  def render(self):
    """
    generates XHTML code

    @rtype: basestring
    @return: XHTML element
    """
    r = []
    for key in self._allowed:
      l = self._lists[key]
      for element in l:
        r.append('%s' % element.render())
    if self._content:
      r.append('%s' % self._content)
    if _MINIMIZE:
      sep = ''
    else:
      sep = '\n'
    return self.element(self._root, self._attrs_data, sep.join(r), self._comment, sep=self._separator)


class Table(Element):
  """
  generates a table
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['thead', 'tfoot', 'tbody', 'tr']

  # the highest (root) element
  _root = 'table'

  def __init__(self, data=[], attrs=[], comment=None):
    """
    constructor
    example of data in Element.__init__

    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'thead': [],
      'tbody': [],
      'tfoot': [],
      'tr': []
    }

    self._elements = {
      'thead': THead,
      'tbody': TBody,
      'tfoot': TFoot,
      'tr': TRow
    }

    Element.__init__(self, data, attrs, comment)


class THead(Element):
  """
  generates a table header
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['tr']

  # the highest (root) element
  _root = 'thead'

  def __init__(self, data=[], attrs=[], comment=None):
    """
    constructor
    example of data in Element.__init__

    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'tr': [],
    }

    self._elements = {
      'tr': TRow,
    }

    Element.__init__(self, data, attrs, comment)


class TFoot(THead):
  """
  generates a table footer
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['tr']

  # the highest (root) element
  _root = 'tfoot'


class TBody(THead):
  """
  generates a table body
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['tr']

  # the highest (root) element
  _root = 'tbody'


class TRow(Element):
  """
  generates a table row
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['td', 'th']

  # the highest (root) element
  _root = 'tr'

  def __init__(self, data=[], attrs=[], comment=None):
    """
    constructor
    example of data in Element.__init__

    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'td': [],
      'th': []
    }

    self._elements = {
      'td': TCell,
      'th': THCell
    }

    Element.__init__(self, data, attrs, comment)


class TCell(Element):
  """
  generates a table cell
  """
  # separator for Base.element()
  _separator = ''

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = []

  # the highest (root) element
  _root = 'td'


class THCell(Element):
  """
  generates a table header cell
  """
  # separator for Base.element()
  _separator = ''

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = []

  # the highest (root) element
  _root = 'th'


class Select(Element):
  """
  generates a select
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['option', 'optgroup']

  # the highest (root) element
  _root = 'select'

  def __init__(self, name, options=[], selected=[], attrs=[], comment=None):
    """
    constructor
    if you want multiple select, set attrs=[['multiple']]
    examples of options:
      options = [
        (value1, content1, attr1.1, attr1.2, ...),
        (value2, content2, attr2.1, attr2.2, ...),
      ]
      options = [1, 2, 3, 4, ...]  # for example for days/months/years etc

    @type name: str
    @param name: name of field
    @type options: basestring|list|tuple|dict|OrderedDict
    @param options: options of the select
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'option': [],
      'optgroup': []
    }

    self._elements = {
      'option': Option,
      'optgroup': Optgroup
    }

    self._selected_values = selected

    # attributes of an element 'select'
    a = [('name', name)]
    if isinstance(attrs, basestring):
      a.extend([attrs])
    elif isinstance(attrs, (list, tuple)):
      a.extend(attrs)
    else:  # dict/OrderedDict
      for k in attrs:
        a.append((k, attrs[k]))

    Element.__init__(self, [], a, comment)

    if options:
      self.options(options)

  def option(self, value, content=None, selected=None, attrs=[], comment=None):
    """
    appends an option to the select

    @type value: basestring
    @param value: value of attribute
    @type content: basestring|None
    @param content: content of the option (content of the element), if None content=value
    @type selected: None|bool|int
    @param selected: True/False/1/0
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: Option
    @return: returns the appended option
    """
    tag = 'option'
    l = self._lists.get(tag)
    c = self._elements.get(tag)
    if selected is None:
      s = (value in self._selected_values)
    else:
      s = selected
    l.append(c(value, content, s, attrs, comment))
    return l[-1]

  def options(self, data, selected=[]):
    """
    extends the select of options
    examples of data:
      data = [
        (value1, content1, attr1.1, attr1.2, ...),
        (value2, content2, attr2.1, attr2.2, ...),
      ]
      data = [1, 2, 3, 4, ...]  # for example for days/months/years etc

    @type data: list|tuple
    @param data: list of options
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @rtype: Select
    @return: returns self
    """
    if selected:
      sel = selected
    else:
      sel = self._selected_values
    if not isinstance(sel, (list, tuple)):
      sel = [sel]
    for i in data:
      if isinstance(i, (list, tuple)):
        v = i[0]
        if len(i) == 1:
          t = i[0]
        else:
          t = i[1]
        a = i[2:]
      else:  # basestring/int/float
        v = i
        t = None
        a = []
      s = (v in sel)
      self.option(v, t, s, a)
    return self

  def optgroup(self, label, options=[], selected=[], attrs=[], comment=None):
    """
    appends an optgroup to the select
    examples of options:
      options = [
        (value1, content1, attr1.1, attr1.2, ...),
        (value2, content2, attr2.1, attr2.2, ...),
      ]
      options = [1, 2, 3, 4, ...]  # for example for days/months/years etc

    @type label: basestring
    @param label: title of optgroup
    @type options: basestring|list|tuple|dict|OrderedDict
    @param options: options of the optgroup
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    tag = 'optgroup'
    l = self._lists.get(tag)
    c = self._elements.get(tag)
    if selected:
      sel = selected
    else:
      sel = self._selected_values
    if not isinstance(sel, (list, tuple)):
      sel = [sel]
    l.append(c(label, options, sel, attrs, comment))
    return l[-1]


class Optgroup(Select):
  """
  generates a table row
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['option']

  # the highest (root) element
  _root = 'optgroup'

  def __init__(self, label, options=[], selected=[], attrs=[], comment=None):
    """
    constructor
    examples of options:
      options = [
        (value1, content1, attr1.1, attr1.2, ...),
        (value2, content2, attr2.1, attr2.2, ...),
      ]
      options = [1, 2, 3, 4, ...]  # for example for days/months/years etc

    @type label: basestring
    @param label: title of optgroup
    @type options: basestring|list|tuple|dict|OrderedDict
    @param options: options of the optgroup
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'option': []
    }

    self._elements = {
      'option': Option
    }

    self._selected_values = selected

    # attributes of an element 'select'
    a = [('label', label)]
    if isinstance(attrs, basestring):
      a.extend([attrs])
    elif isinstance(attrs, (list, tuple)):
      a.extend(attrs)
    else:  # dict/OrderedDict
      for k in attrs:
        a.append((k, attrs[k]))

    Element.__init__(self, [], a, comment)

    if options:
      self.options(options)


class Option(Element):
  """
  generates an option for select
  """
  # separator for Base.element()
  _separator = ''

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = []

  # the highest (root) element
  _root = 'option'

  def __init__(self, value, content=None, selected=False, attrs=[], comment=None):
    """
    constructor

    @type value: basestring
    @param value: value of attribute
    @type content: basestring|None
    @param content: content of the option (content of the element), if None content=value
    @type selected: bool|int
    @param selected: True/False/1/0
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    v = '%s' % value
    if content:
      c = '%s' % content
    else:
      c = v

    self._selected_value = None

    # attributes of an element 'option'
    a = [('value', v)]
    if isinstance(attrs, basestring):
      a.extend([attrs])
    elif isinstance(attrs, (list, tuple)):
      a.extend(attrs)
    else:  # dict/OrderedDict
      for k in attrs:
        a.append((k, attrs[k]))

    Element.__init__(self, c, a, comment)

    self.selected(selected)

  def selected(self, value=None):
    """
    sets selected or just returns its value

    @type value: None|bool
    @param value: with bool you can change the value, None just returns the value
    @rtype: Option|bool
    @return: returns self
    """
    if value is None:
      return self._selected_value
    else:
      v = bool(value)
      self._selected_value = v
      return self

  def render(self):
    """
    generates XHTML code

    @rtype: basestring
    @return: XHTML element
    """
    # removes attribute selected - sets it by self._selected_value
    if isinstance(self._attrs_data, tuple):
      self._attrs_data = list(self._attrs_data)
    x = 0
    for i in self._attrs_data[:]:
      if isinstance(i, (list, tuple)) and i[0] == 'selected':
        self._attrs_data.pop(x)
        # no break, there can be duplicate selected attributes
      x += 1

    if self.selected():
      # sets attribute selected before rendering
      self.attr('selected', 'selected')

    return Element.render(self)


class Ul(Element):
  """
  generates an unordered list
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['li']

  # the highest (root) element
  _root = 'ul'

  def __init__(self, data=[], attrs=[], comment=None):
    """
    constructor
    example of data in self.lis

    @type data: basestring|list|tuple
    @param data: data of element
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    """
    self._lists = {
      'li': []
    }

    self._elements = {
      'li': Li
    }

    Element.__init__(self, [], attrs, comment)

    if data:
      self.lis(data)

  def li(self, content=None, attrs=[], comment=None):
    """
    appends an list item

    @type content: basestring|None
    @param content: content of the option (content of the element), if None content=value
    @type attrs: basestring|list|tuple|dict|OrderedDict
    @param attrs: attributes
    @type comment: None|basestring
    @param comment: <!-- /something --> behind the tag
    @rtype: Li
    @return: returns the appended li
    """
    tag = 'li'
    l = self._lists.get(tag)
    c = self._elements.get(tag)
    l.append(c(content, attrs, comment))
    return l[-1]

  def lis(self, data, selected=[]):
    """
    extends the list of items
    examples of data:
      data = [
        (content1, attr1.1, attr1.2, ...),
        (content2, attr2.1, attr2.2, ...),
      ]
      data = ['1', '2', '3', '4', ...]
      data = {content1: [attr1.1, attr1.2, ...]}

    @type data: list|tuple
    @param data: list of options
    @type selected: basestring|list|tuple
    @param selected: selected values of field
    @rtype: Select
    @return: returns self
    """
    l = ''

    if isinstance(data, basestring):
      l = data
    elif isinstance(data, (list, tuple)):
      for i in data:
        if isinstance(i, (list, tuple)):
          t = i[0]
          a = []
          if len(i) > 1:
            a = i[1:]
          self.li(t, a)
        else:  # basestring/int/float etc
          self.li('%s' % i)
    else:  # dict/OrderedDict
      [self.li(k, data[k]) for k in data]

    return self


class Ol(Ul):
  """
  generates an ordered list
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['li']

  # the highest (root) element
  _root = 'ol'


class Dir(Ul):
  """
  generates a list directory titles
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['li']

  # the highest (root) element
  _root = 'dir'


class Menu(Ul):
  """
  generates a list of menu choices
  """

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = ['li']

  # the highest (root) element
  _root = 'menu'


class Li(Element):
  """
  generates a list item
  """
  # separator for Base.element()
  _separator = ''

  # allowed subitems
  # - in this order it is generated with render()
  _allowed = []

  # the highest (root) element
  _root = 'li'

