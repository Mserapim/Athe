def purge_site(slug):
    from web.models import Area

    for site in Area.objects.filter(slug=slug):
        print("deletando site: ", site.name)
        for area in site.children.all():
            print("\tdeletando area: ", area.fullname)
            for content in area.contents.all():
                print("\t\tdeletando conteudo: ", content.title)
                if hasattr(content, "post"):
                    print("\t\t\tdeletando anexos")
                    for f in content.post.files.all():
                        f.delete()
                    for i in content.post.images.all():
                        i.delete()
                    for a in content.post.audios.all():
                        a.delete()
                    for v in content.post.videos.all():
                        v.delete()
                content.delete()
            area.delete()
        site.delete()
