import { baseDatasourceFactory } from './base.datasource.factory';
import { apiRhPvfVendaSubstituicoes } from 'api/rh/api-rh-pvf-venda-substituicoes.service';

export class RhPvfapiRhPvfVendaSubstituicoesDataSource extends baseDatasourceFactory(
    apiRhPvfVendaSubstituicoes
) {}
