from django.contrib import admin
from django import forms
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


class ProductAdminForm(forms.ModelForm):
    sizes_input = forms.CharField(
        required=False,
        label='Sizes (comma-separated)',
        help_text='e.g. XS, S, M, L, XL',
        widget=forms.TextInput(attrs={'placeholder': 'XS, S, M, L, XL'}),
    )
    unavailable_sizes_input = forms.CharField(
        required=False,
        label='Unavailable sizes (comma-separated)',
        help_text='Sizes that are sold out — will be shown crossed out on the site. e.g. XS, M',
        widget=forms.TextInput(attrs={'placeholder': 'XS, M'}),
    )
    colors_input = forms.CharField(
        required=False,
        label='Colors (comma-separated)',
        help_text='e.g. Black, White, Grey',
        widget=forms.TextInput(attrs={'placeholder': 'Black, White, Grey'}),
    )

    class Meta:
        model = Product
        exclude = ['sizes', 'unavailable_sizes', 'colors']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            sizes = self.instance.sizes or []
            unavailable = self.instance.unavailable_sizes or []
            colors = self.instance.colors or []
            self.fields['sizes_input'].initial = ', '.join(sizes)
            self.fields['unavailable_sizes_input'].initial = ', '.join(unavailable)
            self.fields['colors_input'].initial = ', '.join(colors)

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw_sizes = self.cleaned_data.get('sizes_input', '')
        raw_unavailable = self.cleaned_data.get('unavailable_sizes_input', '')
        raw_colors = self.cleaned_data.get('colors_input', '')
        instance.sizes = [s.strip() for s in raw_sizes.split(',') if s.strip()] if raw_sizes else []
        instance.unavailable_sizes = [s.strip() for s in raw_unavailable.split(',') if s.strip()] if raw_unavailable else []
        instance.colors = [c.strip() for c in raw_colors.split(',') if c.strip()] if raw_colors else []
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'category', 'gender', 'price', 'stock', 'is_active', 'is_new', 'created_at']
    list_filter = ['category', 'gender', 'is_active', 'is_new']
    list_editable = ['is_active', 'is_new', 'stock']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {'fields': ('category', 'gender', 'name', 'slug', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'stock', 'is_active', 'is_new')}),
        ('Variants', {'fields': ('sizes_input', 'unavailable_sizes_input', 'colors_input')}),
    )
