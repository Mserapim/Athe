import { Route } from '@angular/router';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponent } from './vdf-solicitacao-teletrabalho-desbloqueio-criar.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-step1/vdf-solicitacao-teletrabalho-desbloqueio-criar-step1.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep2Component } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-step2/vdf-solicitacao-teletrabalho-desbloqueio-criar-step2.component';

export const VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponentRoute: Route[] =
    [
        {
            path: 'solicitacoes/novo/teletrabalho-desbloqueio',
            component: VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponent,
            children: [
                {
                    path: 'step1',
                    component:
                        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component,
                },
                {
                    path: 'step2',
                    component:
                        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep2Component,
                },
            ],
        },
    ];
