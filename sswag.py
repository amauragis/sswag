#!/usr/bin/env python3

import os
import collections

import jinja2 as jinja
import markdown
import markdown.extensions.meta
from shutil import copy2

import logger
import sswag_config as configs


def main():
    # make output directory
    os.makedirs(configs.www_root, exist_ok=True)

    # generate templates and page metadata
    templates = get_templates(configs.template_path)
    page_data = get_page_data(configs.pages_path)

    page_data = generate_galleries(page_data)

    # render markdown + templates to html
    markdown_render(page_data, templates)

    # Put all static content into the html folder
    logger.info('Copying static content...')
    for dirpath, dirnames, filenames in os.walk(configs.static_path):
        # Create the mirrored folders in the html directory
        if len(dirnames) > 0:
            for dirname in dirnames:
                path = os.path.join(dirpath, dirname)
                # XXX: don't do this stupid hack. rebuild the directory structure
                path = configs.www_root + path[6:]  # remove the static in front of the path, replace it with www root
                os.makedirs(path, exist_ok=True)

        if len(filenames) > 0:
            for filename in filenames:
                ext = os.path.splitext(filename)[1]

                spath = os.path.join(dirpath, filename)
                dpath = 'html' + spath[6:]
                if ext in [
                    '.css', '.js', '.ttf', '.eot', '.svg', '.woff', '.png',
                    '.pdf', '.pptx', '.doc', '.txt', '.gz', '.tgz', '.jpg',
                    '.ico', '.gif',
                ]:
                    # These do not need to be compiled in any way
                    # Just copy them
                    logger.debug('Copying file: ' + spath)
                    copy2(spath, dpath)
                else:
                    logger.debug('Skipping file: ' + spath)


def get_templates(template_path):
    # get all of the template files
    templates = dict()
    jinja_env = jinja.Environment(loader=jinja.FileSystemLoader(template_path))
    for file_path in os.listdir(template_path):
        base, extension = os.path.splitext(file_path)
        if extension == '.html':
            logger.info('Found template: ' + base + extension)
            templates[base] = jinja_env.get_template(base + extension)

    logger.debug('Templates: ' + str(templates))
    return templates


def get_page_data(markdown_path):
    # get all markdown files in pages
    md_pages = list()
    for file_path in os.listdir(markdown_path):
        base, extension = os.path.splitext(file_path)
        if extension == '.md':
            logger.info('Found page: ' + base + extension)
            md_pages.append(base)

    logger.debug('Pages: ' + str(md_pages))

    # parse all of the markdown into page data dict
    md = markdown.Markdown(extensions=['markdown.extensions.meta'])
    page_data = dict()
    for md_page in md_pages:
        logger.info('Parsing page: ' + md_page)
        page_path = os.path.join(markdown_path, md_page + ".md")
        page_data[md_page] = dict()

        # store html and metadata
        page_data[md_page]['html_content'] = md.convert(open(page_path).read())
        page_data[md_page]['meta'] = md.Meta
        logger.debug('page: ' + md_page + '\n\t\tmeta:' + str(page_data[md_page]['meta']))

    return page_data


def generate_galleries(page_data):
    galleries_root = os.path.join(configs.www_root, 'galleries')

    for page in page_data:
        try:
            gallery_path = page_data[page]['meta']['gallerypath'][0]
        except KeyError:
            continue

        logger.info('Generating gallery info for ' + page)
        gallery_images = list()

        # TODO: generate thumbnails and add them to the page_data dict
        for filename in os.listdir(gallery_path):
            ext = os.path.splitext(filename)[1]

            if ext.lower() in [
                '.png', '.jpg', '.jpeg', '.gif',
            ]:
                # copy image files from metadata specified gallery path to the gallery root
                spath = os.path.join(gallery_path, filename)
                dpath = os.path.join(galleries_root, gallery_path)
                os.makedirs(dpath, exist_ok=True)
                logger.debug('Copying file from ' + spath + ' to ' + dpath)
                copy2(spath, dpath)
                html_path = os.path.relpath(os.path.join(dpath, filename), configs.www_root)
                gallery_images.append(html_path)

            else:
                logger.debug('Skipping gallery file: ' + filename)

        page_data[page]['images'] = gallery_images

    return page_data


def markdown_render(page_data, templates):
    # create the navbar dict
    navbar_pages = collections.OrderedDict()
    for page, data in sorted(page_data.items(), key=lambda x: int(x[1]['meta'].get('order', ['100'])[0])):
        show_in_navbar = data['meta'].get('show_in_navbar', ['True'])
        if show_in_navbar[0] in ['true', 'True', 1]:
            logger.debug('Navbar entry: {}'.format(page))
            page_title = data['meta'].get('title', page)
            navbar_pages[page] = page_title

    logger.debug('Navbar dict: {0!s}'.format(navbar_pages))
    for page in page_data:
        logger.info('Rendering page: ' + page)
        template = None
        try:
            logger.debug('  with template: {}'.format(page_data[page]['meta']['template'][0]))
            if page_data[page]['meta']['template'][0] in list(templates.keys()):
                template = templates[page_data[page]['meta']['template'][0]]

        except KeyError:
            logger.warn('Failed to get template for ' + page)
            continue

        # TODO: use configured www_root
        with open('html/{}.html'.format(page), 'w') as o:
            logger.debug('Writing html to html/{}.html'.format(page))
            logger.debug('Template parameters:\n'
                         '\t\tactive_page: {0}\n'
                         '\t\tpage_content: <skipped>\n'
                         '\t\tcontact_info: <skipped>\n'
                         '\t\tpages: {1!s}\n'.format(page, navbar_pages))
            if 'images' in page_data[page]:
                rendered_page = template.render(active_page=page, page_content=page_data[page]['html_content'],
                                                pages=navbar_pages, images=page_data[page]['images'])
                logger.debug('Images: {0!s}'.format(page_data[page]['images']))
            else:
                rendered_page = template.render(active_page=page, page_content=page_data[page]['html_content'],
                                                pages=navbar_pages)

            o.write(rendered_page)


if __name__ == "__main__":
    main()
