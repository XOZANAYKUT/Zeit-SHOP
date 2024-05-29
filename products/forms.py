from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Rating, Comment



class CommentForm(forms.ModelForm):
    """
    Form class for users to comment on a product
    """
    class Meta:
        """
        Specify the django model and order of the fields
        """
        model = Comment
        fields = ('body',)


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score',]
        widgets = {
            'score': forms.RadioSelect,
        }

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

class AddToWishlistForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())