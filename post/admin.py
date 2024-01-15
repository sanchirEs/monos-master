"""
Post's admin.

created by Mezorn LLC
"""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from post.models import Post, AdvicePost
from monosbot.celery_scheduled_tasks import fetch_post_meta_data_sync_onform


ALLOWED_GROUPIDS = ['154243908530765', '1272597072788273', '2149422908642584']

ALLOWED_URLS = ['https://monos.workplace.com/groups/154243908530765/permalink/', 'https://monos.workplace.com/groups/1272597072788273/permalink/', 'https://monos.workplace.com/groups/2149422908642584/permalink/']


class PostForm(forms.ModelForm):
    """ post form """
    class Meta:
        """ meta """
        model = Post

        fields = ('post_url', 'post_name', 'facebook_id', 'related_campaing', 'image_url', 'like_count', 'comment_count', 'refetch_data')

        # def clean(self):
        #     start_date = self.cleaned_data.get('start_date')
        #     end_date = self.cleaned_data.get('end_date')
        #     if start_date > end_date:
        #         raise forms.ValidationError("Dates are incorrect")
        # return self.cleaned_data

    def clean(self):
        """#run the standard clean method first"""
        form_data = super(PostForm, self).clean()

        post_url = form_data['post_url']

        should_fetch = form_data['refetch_data']

        fetch = False

        if self.instance.pk is None or should_fetch:

            fetch = True

        if not fetch and post_url != self.instance.post_url:

            fetch = True

        if fetch:

            group_id = ''

            initial_url = ''

            i = 0

            for url in ALLOWED_URLS:

                if url in post_url:

                    group_id = ALLOWED_GROUPIDS[i]

                    initial_url = url

                    break

                i += 1

            if not group_id:

                raise ValidationError("URL буруу байна. monos.facebook.com - д хамааралтай пост оруулна уу", code=101)

            try:

                int(post_url.replace(initial_url, '').replace('/', ''))

            except ValueError:

                raise ValidationError("URL буруу байна. Постын url аа зөв оруулна уу", code=101)

        return form_data


class PostAdmin(admin.ModelAdmin):
    """
    Post's admin class.
    """

    form = PostForm

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('short_description', 'facebook_id', 'related_campaing')

    list_display_links = ('short_description', 'facebook_id',)

    list_filter = ('related_campaing__product_name',)

    readonly_fields = ('post_name', 'facebook_id', 'image_url', 'like_count', 'comment_count')

    search_fields = ['post_name', 'facebook_id']


class AdvicePostAdmin(admin.ModelAdmin):
    """
    Post's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('short_description', 'manager_name', 'facebook_id',)

    list_display_links = ('short_description', 'manager_name', 'facebook_id',)

    list_filter = ('related_campaing__product_name', 'related_manager__fullname')

    readonly_fields = ('post_name', 'post_url', 'facebook_id', 'related_campaing', 'related_manager', 'image_url', 'like_count', 'comment_count')

    fields = ('post_name', 'facebook_id', 'group_id', 'related_campaing', 'related_manager', 'post_url', 'image_url', 'like_count', 'comment_count')

    search_fields = ['post_name', 'facebook_id']


admin.site.register(Post, PostAdmin)

admin.site.register(AdvicePost, AdvicePostAdmin)
