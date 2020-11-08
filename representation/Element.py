from enum import Enum, auto 

class Location(Enum):
    top_left = 'top_left'
    top_right = 'top_right'
    bottom_left = 'bottom_left'
    bottom_right = 'bottom_right'
    top = 'top'
    bottom = 'bottom'
    left = 'left'
    right = 'right'
    none = ''

class Type(Enum):
    button = 'button'
    link = 'link'
    input_el = 'input'
    checkbox = 'checkbox'
    dropdown = 'dropdown'
    image = 'image'
    icon = 'icon'
    text = 'text'
    none = ''
    
class Element:
# get the data and compute the additional representations here
    def __init__(self, attrs, embedding_model):
        # print (attrs)
        self.location = Location.none
        self.type = Type.none
        self.right = []
        self.left = [] 
        self.bottom = [] 
        self.above = [] 
        self.attributes = ''
        self.selector = ''
        self.text = ''
        self.class_id = ''
        self.attributes = ''
        self.tag = ''
        self.role = ''
        self.hidden = False
        self.top = 0
        self.left = 0
        self.width = 0
        self.height = 0
        self.children = []
        self.text_emb = np.zeros(768)
        if 'ref' in attrs.keys() and attrs['ref'] is not None:
            self.ref = attrs['ref']
        if 'xid' in attrs.keys() and attrs['xid'] is not None:
            self.xid = attrs['xid']
        if 'selector' in attrs.keys():
            self.selector = attrs['selector']
        if 'text' in attrs.keys():
            self.text = attrs['text']

        self.class_id = ''
        if 'classes' in attrs.keys() and attrs['classes'] is not None:
            self.class_id  += attrs['classes'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'id' in attrs.keys() and attrs['id'] is not None:
            self.class_id  += attrs['id'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'tag' in attrs.keys() and attrs['tag'] is not None:
            self.tag = attrs['tag']

        if 'attributes' in attrs.keys() and attrs['attributes'] is not None:
            for key, value in attrs['attributes'].items():
                if key == 'class':
                    continue
                self.attributes += key.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
                self.attributes += value.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'role' in attrs.keys() and attrs['role'] is not None:
            self.role = attrs['role']
        if 'hidden' in attrs.keys() and attrs['hidden'] is not None:
            self.hidden = attrs['hidden']
        if 'top' in attrs.keys() and attrs['top'] is not None:
            self.top = attrs['top']
        if 'left' in attrs.keys() and attrs['left'] is not None:
            self.top = attrs['left']
        if 'width' in attrs.keys() and attrs['width'] is not None:
            self.top = attrs['width']
        if 'height' in attrs.keys() and attrs['height'] is not None:
            self.top = attrs['height']
        if 'children' in attrs.keys() and attrs['children'] is not None:
            self.top = attrs['children']
        if self.text != '':
            self.text_emb = embedding_model.encode([self.text])[0]
        # TODO: compute Location, size, childof