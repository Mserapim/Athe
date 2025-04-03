import { apiRhPvfMinhasAnotacoes } from 'api/rh/api-rh-pvf-minhas-anotacoes.service';
import { baseDatasourceFactory } from './base.datasource.factory';

export class RhPvfMinhasAnotacoesDataSource extends baseDatasourceFactory(
    apiRhPvfMinhasAnotacoes
) {}
