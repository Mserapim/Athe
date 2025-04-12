from rh.gfp.models import MovimentacaoProgressao
from contrib.middleware import set_current_user
import datetime

set_current_user("athenas")
date = datetime.datetime(2018, 1, 1)
query = MovimentacaoProgressao.objects.filter(created_at__gte=date)
count = 0
total = query.count()
for q in query.order_by("servidor"):
    q.anotacao()
    count += 1
    print(q.servidor, q)
    print("count %s => total %s" % (count, total))
