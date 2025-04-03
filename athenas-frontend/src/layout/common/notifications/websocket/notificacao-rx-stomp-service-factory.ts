import { NotificacaoRxStompService } from './notificacao-rx-stomp.service';
import { NotificacaoRxStompConfig } from './notificacao-rx-stomp.config';

export function NotificacaoRxStompServiceFactory() {
  const rxStomp = new NotificacaoRxStompService();
  rxStomp.configure(NotificacaoRxStompConfig);
  rxStomp.activate();
  return rxStomp;
}