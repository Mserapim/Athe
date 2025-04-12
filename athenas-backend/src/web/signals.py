from django.db.models.signals import post_save
from rh.models import PessoaFisica


def sync_rh_email(sender, instance, **kwargs):

    if hasattr(instance.pessoa_ptr, "web_user") and not getattr(
        instance, "_skip_signal", False
    ):
        web_user = instance.pessoa_ptr.web_user
        web_user.email = (
            instance.email_institucional.lower()
            if instance.email_institucional
            else None
        )
        web_user.save()


post_save.connect(sync_rh_email, PessoaFisica)
