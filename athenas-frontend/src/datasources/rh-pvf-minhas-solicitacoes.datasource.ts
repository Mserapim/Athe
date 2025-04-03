import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhPvfMinhasSolicitacoes } from 'api/rh/api-rh-pvf-minhas-substituicoes.service';

export class RhPvfMinhasSolicitacoesDataSource extends baseDatasourceFactory(
    apiRhPvfMinhasSolicitacoes
) {}
