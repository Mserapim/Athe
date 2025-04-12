from web import models
from web.exporter import files
import importlib


def export_files(flush=False):
    importlib.reload(models)
    importlib.reload(files)

    if flush:
        for p in models.Post.objects.filter(
            areas__parent__slug="transparencia-test", areas__slug="paginas"
        ):
            for f in p.files.all():
                f.delete()
            p.delete()

        for l in models.Link.objects.filter(
            areas__parent__slug="transparencia-test",
            areas__slug="menu-esquerdo",
            parent__isnull=False,
        ):
            try:
                l.delete()
            except Exception:
                pass
    files.main()


def copy_files():
    for p in models.Post.objects.filter(
        areas__parent__slug="transparencia",
        areas__slug="paginas",
        slug__icontains="relatorios-recursos-humanos-exercicio-2010-",
    ):
        title = p.title
        print(title)
        try:
            p2 = models.Post.objects.get(
                areas__parent__slug="transparencia-test",
                areas__slug="paginas",
                title=str(title),
            )
            for f in p2.files.filter(active=True):
                ff = p.files.get(title=f.title)
                ff.delete()
                p.files.add(f)
        except Exception as e:
            print(e, title)
            print("")
