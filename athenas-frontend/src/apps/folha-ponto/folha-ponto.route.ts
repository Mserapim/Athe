import { Route } from '@angular/router';
import { VdfFolhaPontoComponent } from 'apps/vdf/vdf-folha-ponto/vdf-folha-ponto.component';

export const FolhaPontoRoute: Route[] = [
    {
        path: 'folha-ponto',
        component: VdfFolhaPontoComponent,
    }
];
