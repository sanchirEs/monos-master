"""
Online test's models.

created by Mezorn LLC
"""

from django.db import models
from campaign.models import Campaign


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super(BaseModelManager, self).get_queryset().filter(is_active=True)


class BaseModelTest(models.Model):

    """
    Base model
    """
    objects = BaseModelManager()

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Class meta
        """
        abstract = True

class BaseModel(models.Model):

    """
    Base model
    """

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Class meta
        """
        abstract = True


class OnlineTest(BaseModel):

    """
    Online test's model
    """

    test_name = models.CharField(max_length=200, default='', verbose_name='Тестийн нэр')

    related_campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, default=None, verbose_name='Хамаарах хөтөлбөр', related_name='current_test')

    is_active = models.BooleanField(default=False, verbose_name='Идэвхитэй эсэх')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Тест'

        verbose_name_plural = 'Тестүүд'

        ordering = ['-created_date']

    def __str__(self):

        return self.test_name

    def save(self, *args, **kwargs):

        from monos.common import check_and_set_current_campaign

        super(OnlineTest, self).save(*args, **kwargs)
        
        check_and_set_current_campaign(self.related_campaign)


class OnlineTestQuestion(BaseModel):

    """
    Online test question's model
    """

    order = models.IntegerField(default=0, verbose_name='Дугаар', blank=True)

    question = models.CharField(max_length=200, default='', verbose_name='Асуулт')

    related_test = models.ForeignKey(OnlineTest, default=None, related_name='questions', on_delete=models.CASCADE, verbose_name='Хамаарах тест')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Асуулт'

        verbose_name_plural = 'Асуултууд'

        ordering = ['order']

    def __str__(self):

        return self.question

    def save(self, *args, **kwargs):

        from monos.common import check_and_set_current_campaign

        if self.id is None:

            current_count = 0

            last_question = self.related_test.questions.all().order_by('order').last()

            if last_question:

                current_count = last_question.order

            self.order = current_count + 1

        super(OnlineTestQuestion, self).save(*args, **kwargs)

        self.related_test.related_campaign.calculate_total_xp()

        if self.related_test.is_active is True:
            check_and_set_current_campaign(self.related_test.related_campaign)

class OnlineTestAnswer(BaseModel):

    """
    Online test answers's model
    """

    question = models.ForeignKey(OnlineTestQuestion, default=None, on_delete=models.CASCADE, related_name='answers')

    short_answer = models.CharField(max_length=1, default='', verbose_name='Богино хариулт')

    full_answer = models.TextField(default='', verbose_name='Бүтэн хариулт')

    is_correct = models.BooleanField(default=False, verbose_name='Зөв хариулт эсэх')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Хариулт'

        verbose_name_plural = 'Хариултууд'

        ordering = ['short_answer', '-created_date']

    def __str__(self):

        return self.question.question + ' - ' + self.short_answer

    def save(self, *args, **kwargs):

        from monos.common import check_and_set_current_campaign

        super(OnlineTestAnswer, self).save(*args, **kwargs)

        # print("in save")

        # test = self.question.related_test

        # questions = OnlineTestQuestion.objects.filter(related_test=test)

        # print(questions.count())

        # all_questions_has_answer = True

        # for q in questions:

        #     answers = OnlineTestAnswer.objects.filter(question=q)

        #     if not answers:

        #         all_questions_has_answer = False
        
        # print(all_questions_has_answer)

        # if all_questions_has_answer:
            
        #     test.is_active = True

        #     test.save()

        check_and_set_current_campaign(self.question.related_test.related_campaign)
