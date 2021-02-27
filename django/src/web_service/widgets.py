from django import forms
from django.urls import reverse_lazy

class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'widgets/custom_base.html'
    option_template_name = 'widgets/custom_checkbox_option.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)

        if 'class' in self.attrs:
            self.attrs['class'] += ' custom-checkbox'
        else:
            self.attrs['class'] = 'custom-checkbox'

class UploadableTextarea(forms.Textarea):
    class Media:
        js = ['js/blog_file_upload.js']

    def __init__(self, attrs=None):
        super().__init__(attrs)

        if 'class' in self.attrs:
            self.attrs['class'] += ' uploadable vLargeTextField'
        else:
            self.attrs['class'] = 'uploadable vLargeTextField'
        self.attrs['data-url'] = reverse_lazy('blog:image_upload')
