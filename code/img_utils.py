import pathlib
import urllib.request
import io
from PIL import Image



def get_image_with_url(image_url, save_image=False, title='Unknown', score=0, binary=False, size=()):

    try:
        if len(title.split(" ")) > 1:
            title = title.replace(" ", "-")
        if len(title.split(",")) > 1:
            title = title.replace(",", "-")
        title = title.lower()
        image_save_dir = pathlib.Path.cwd().parent / 'data' / 'downloads' / title
        image_save_dir.mkdir(parents=True, exist_ok=True)
        if 'bing' in image_url:
            image_filename = image_url.split('/')[-1].split('.')[-1].split('&')[0]
            extension = '.jpg'
        else:
            image_filename = image_url.split('/')[-1].split('.')[0]
            extension = '.' + image_url.split('.')[-1]
        if score:
            image_filename = image_filename + ' ' + str(score).replace('.', '_')

        if not image_url.startswith('http'):
            image_url = 'https:' + image_url
        bin_image = urllib.request.urlopen(image_url).read()

        if binary and (not save_image):
            return bin_image
        
        piled = False
        try:
            image = Image.open(io.BytesIO(bin_image))
            if size:
                image = image.resize(size, Image.LANCZOS)
                resized = True
            piled = True
        except Exception as e:
            print(e)

        if save_image:
            with open(str(image_save_dir) + '/' + image_filename + extension, 'wb') as image_file:
                if piled:
                    image.save(image_file)
                else:
                    image_file.write(bin_image)

                image_file.close()

        if binary:
            return bin_image
        else:
            return image

    except Exception as e:
        print(e)
    return