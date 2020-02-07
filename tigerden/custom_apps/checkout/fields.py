from django import forms

class ListTextWidget(forms.TextInput):
    """
    Textfield with options in datalist
    See usage at https://stackoverflow.com/a/32791625/9499790
    """
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list': 'list__{}'.format(self._name)})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__{}">'.format(self._name)
        for item in self._list:
            data_list += '<option data-value="{}" value="{}"></option>'.format(item[0], item[1])
        data_list += '</datalist>'

        return text_html + data_list