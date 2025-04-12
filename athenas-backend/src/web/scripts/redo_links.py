# -*- coding:utf-8 -*-

from web.models import Area, Post, Link
from django.conf import settings


def _links_for_areas():
    print("---------------------------")
    print("Correcting links for areas")
    print("---------------------------\n")
    for link in Link.objects.filter(active=True, kind=2):
        try:
            print("Current url: %s" % link.url_embed)
            area = Area.objects.get(slug=link.url_embed)
            link.url_embed = area.get_absolute_url()
            link.save()
            print("Correct url: %s" % link.url_embed)
        except Exception as e:
            print("Error: %s" % e)
        print(
            "==========================================================================="
        )


def _links_for_posts():
    print("---------------------------")
    print("Correcting links for posts")
    print("---------------------------\n")
    for link in Link.objects.filter(active=True, kind=3):
        try:
            print("Current url: %s" % link.url_embed)
            post = Post.objects.get(slug=link.url_embed)
            link.url_embed = post.get_absolute_url()
            link.save()
            print("Correct url: %s" % link.url_embed)
        except Exception as e:
            print("Error: %s" % e)
        print(
            "==========================================================================="
        )


def self_links_change_domain(old_domain, new_domain):
    for link in Link.objects.filter(
        active=True, kind__in=[1, 2, 3, 4], url_embed__icontains=old_domain
    ):
        try:
            link.url_embed = link.url_embed.replace(
                old_domain, new_domain
            )  #'http://%s/%s' % (new_domain, '/'.join(link.url_embed.split('http://')[1].split('/')[1:]))
            print(link.url_embed)
            link.save()
        except Exception as e:
            print("---------------------------------------")
            print("Error: ", link.url_embed, "=>", e)
            print("---------------------------------------")


# def main():
#     _links_for_areas()
#     _links_for_posts()

# if __name__ == '__main__':
#     main()
