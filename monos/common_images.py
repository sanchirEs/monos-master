"""
Image related methods

created by Mezorn LLC
"""

import os
from django.conf import settings
from PIL import Image, ImageFile

def configure_width(current_image, check_width):
    """
    Configure image width
    """

    if current_image.width > check_width:

        current_image.thumbnail((check_width, 10000), Image.LANCZOS)

    return current_image

def configure_size(current_image, check_size):
    """
    Configure image size
    """

    if current_image.width != check_size[0] or current_image.height != check_size[1]:

        crop_x = 0

        crop_y = 0

        new_width = check_size[0]

        new_height = check_size[1]

        if (current_image.width > new_width and current_image.height > new_height) or (current_image.width < new_width and current_image.height < new_height):

            width_ratio = new_width / current_image.width

            height_ratio = new_height / current_image.height

        elif current_image.width > new_width:

            height_ratio = new_height / current_image.height

            width_ratio = height_ratio - 1

        else:

            width_ratio = new_width / current_image.width

            height_ratio = width_ratio - 1

        if width_ratio > height_ratio:

            new_height = int(current_image.height*width_ratio)

            crop_y = int((new_height - check_size[1])/2)

        else:

            new_width = int(current_image.width * height_ratio)

            crop_x = int((new_width - check_size[0]) / 2)

        current_image = current_image.resize((new_width, new_height), Image.LANCZOS)

        current_image = current_image.crop((crop_x, crop_y, crop_x + check_size[0], crop_y + check_size[1]))

    return current_image

def initial_setup(instance, attribute_name, dir_path, should_save=False, check_width=None, check_size=None):
    """
    Initial image setup
    """

    print('Initial setup reading ... ')

    image_field = getattr(instance, attribute_name)

    initial_path = image_field.path

    new_file_name = attribute_name + '.jpeg'

    image_field.name = dir_path + new_file_name

    new_path = settings.MEDIA_ROOT + image_field.name

    print(initial_path)

    print(image_field.name)

    print(image_field.url)

    print(new_path)

    if os.path.exists(new_path):

        print('New path exists')

        # os.remove(new_path)

    if os.path.exists(initial_path):

        print('Initial exists')

    else:

        print('Initial does not exists')

    os.rename(initial_path, new_path)

    current_image = Image.open(new_path)

    if current_image.mode != 'RGB':

        current_image = current_image.convert('RGB')

    if check_width is not None:

        current_image = configure_width(current_image, check_width)

    if check_size is not None:

        current_image = configure_size(current_image, check_size)

    ImageFile.MAXBLOCK = 2 ** 24

    current_image.save(new_path, "JPEG", quality=90, optimize=True, progressive=True)

    if should_save is True:

        instance.save()

def create_from_image(instance, from_field, image_name, dir_path, size):
    """
    Create image from field
    """

    from_image_field = getattr(instance, from_field)

    from_path = settings.MEDIA_ROOT + from_image_field.name

    new_file_name = image_name + '.jpeg'

    on_path = settings.MEDIA_ROOT + dir_path + new_file_name

    if os.path.exists(on_path):

        os.remove(on_path)

    to_image = Image.open(from_path)

    if to_image.mode != 'RGB':

        to_image = to_image.convert('RGB')

    to_image = configure_size(to_image, size)

    to_image.save(on_path, "JPEG", quality=90, optimize=True, progressive=True)
