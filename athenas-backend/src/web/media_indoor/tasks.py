import os
import shutil
import subprocess
import time

from celery import Celery
from django.conf import settings
from django.contrib.auth.models import User
from PIL import Image

from contrib.utils import getLogger
from default.websocket import RemoteEmmiter
from engine.mq.models import Task
from web.media_indoor.models import Campaign

log = getLogger("media_indoor")
app = Celery("media_indoor")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def transcode_content_task(task, hook, campaign_id, user_id):
    """Esta fução realiza a junção (transcode) de todos os conteúdos da campanha para uma única saída de vídeo

    Args:
    FFMPEG_PATH -- Caminho do executável do FFMPEG
    CODEC_VIDEO -- Formato de codificação do vídeo H.264
    CRF_VIDEO -- '-crf 28'
    TIME_VIDEO -- Slice de vídeo
    PRESET -- Velocidade da Compressão X Qualidade
    FRAME_RATE_VIDEO -- Frames por segundo
    OUTPUT_EXTENSION -- Formato de saída do arquivo de vídeo
    VSYNC -- (option=1) Os frames serão duplicados e descartados para atingir exatamente a taxa de frames constante solicitada.
    ASYNC = -- (async=1) é um caso especial em que apenas o início do stream de áudio é corrigido sem qualquer correção posterior
    VIDEO_SCALE -- Escala do vídeo

    TIME_IMAGE -- Tempo do vídeo gerado para a imagem
    LOOP_IMAGE -- Loop infinito: o tempo determina o término
    FRAME_RATE_IMAGE -- frames da imagem por segundo

    BLANK_AUDIO -- Audio em branco utilizado para a imagem
    CODEC_AUDIO -- Codec de audio
    BITRATE_AUDIO -- Quantidade de bits de audio por segundo

    Raises:
        Exception: raise exveption quando não encontra conteúdos para a campanha
    """

    FFMPEG_PATH = "ffmpeg"

    CODEC_VIDEO = "-c:v libx264"
    CRF_VIDEO = "-crf 22"
    # TIME_VIDEO = '-ss 00:00:00 -to 00:00:10'
    PRESET = "-preset veryfast"
    FRAME_RATE_VIDEO = "-r 30"
    OUTPUT_EXTENSION = ".mp4"
    VSYNC = "-vsync 1"
    ASYNC = "-async 1"
    VIDEO_SCALE = "scale=1920x1080,setsar=1"

    TIME_IMAGE = "-t 15"
    LOOP_IMAGE = "-loop 1"
    FRAME_RATE_IMAGE = "-framerate 5"

    BLANK_AUDIO = f"-f lavfi {TIME_IMAGE} -i anullsrc"
    # CODEC_AUDIO = '-c:a aac'
    # BITRATE_AUDIO = '-b:a 128k'

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        user = User.objects.get(id=user_id)
        campaign = Campaign.objects.get(pk=campaign_id)
        campaign_contents = campaign.campaign_lists.order_by("position")
        if campaign_contents:
            message = f"<p> Gerando conteúdo para a campanha {campaign.name}"
            feedback("", 0, message=message, state=state)
            task.info(
                msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
                type_of=1,
            )

            output_cache_directory = os.path.join(settings.CACHE_PATH, "media_indoor")

            output_file_name = str(campaign.identifier)

            list_input = ""
            map_filter = ""
            filter_complex_partial = ""
            files_to_remove = []

            for count, content_list in enumerate(campaign_contents, start=1):
                file_path = content_list.content.file.absolute_path
                filename = content_list.content.file.filename
                new_filename = filename.replace(" ", "_")

                if not os.path.exists(output_cache_directory):
                    os.makedirs(output_cache_directory)

                original = file_path
                target = os.path.join(output_cache_directory, new_filename)
                shutil.copy(original, target)

                if content_list.content.kind == "image":
                    im = Image.open(target)
                    if im.format == "PNG":
                        rgb_im = im.convert("RGB")
                        new_target = target.replace(".png", ".jpg")
                        rgb_im.save(new_target)
                        files_to_remove.append(
                            os.path.join(output_cache_directory, new_filename)
                        )
                        new_filename = new_target.split("/")[-1]
                    im.close()

                if content_list.content.kind == "image":
                    list_input += f" {LOOP_IMAGE} {TIME_IMAGE} {FRAME_RATE_IMAGE} -i {output_cache_directory}/{new_filename}"
                    map_filter += f"[v{count}][0:a]"
                elif content_list.content.kind == "video":
                    list_input += f" {FRAME_RATE_VIDEO} -i {output_cache_directory}/{new_filename}"
                    map_filter += f"[v{count}][{count}:a]"

                filter_complex_partial += f"[{count}]{VIDEO_SCALE}[v{count}]; "

                files_to_remove.append(
                    os.path.join(output_cache_directory, new_filename)
                )

            qtd_contents = campaign_contents.count()
            concat = f"concat=n={qtd_contents}:v=1:a=1"
            filter_complex = f"{filter_complex_partial} {map_filter} {concat}"

            partial_command = (
                f"{FFMPEG_PATH} {BLANK_AUDIO} {list_input} {CODEC_VIDEO} "
                f"{CRF_VIDEO} {PRESET} {VSYNC} {ASYNC} {FRAME_RATE_VIDEO}"
            )

            cmd = partial_command.split() + [
                "-filter_complex",
                filter_complex,
                "-pix_fmt",
                "yuv420p",
                f"{output_cache_directory}/{output_file_name}{OUTPUT_EXTENSION}",
                "-y",
            ]

            subprocess.run(cmd, check=True, shell=False)

            campaign.active = True
            campaign.save(update_fields=["active"])

            RemoteEmmiter.emmit_for_user(
                user, "media-indoor-transcode-content", campaign_name=campaign.name
            )

            for path in files_to_remove:
                if os.path.isfile(path):
                    os.remove(path)

        else:
            raise Exception("Ocorreu uma falha no processamento dos conteúdos")

    except Campaign.DoesNotExist as e:
        log.exception(e)
        state = "failed"
        has_exception = e
        message = f"<p>A campanha informada não foi encontrada.</p><p>{e}</p>"

    except subprocess.CalledProcessError as e:
        log.exception(e)
        state = "failed"
        has_exception = e
        message = f"<p>Ocorreu um erro no processamento do conteúdo.</p><p>{e}</p>"

    except Exception as e:
        log.exception(e)
        state = "failed"
        has_exception = e
        message = f"<p>Falha na geração do conteúdo da campanha.</p><p>{e}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception
