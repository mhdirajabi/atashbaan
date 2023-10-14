from django.forms import CharField, Form, HiddenInput, ImageField, ModelForm

from .models import Image


class ImageUploadForm(ModelForm):
    image = ImageField(
        required=True,
        max_length=100,
        label="تصویر",
        help_text="لطفاً تصویر مورد نظر خود را از طریق این فرم بارگداری کنید.",
    )

    class Meta:
        model = Image
        fields = [
            "image",
        ]


class SaveProcessedImageForm(Form):
    def __init__(self, *args, **kwargs):
        super(SaveProcessedImageForm, self).__init__(*args, **kwargs)
        self.fields["image"] = CharField(required=False, widget=HiddenInput())
