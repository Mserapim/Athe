import { pvfConfigTiposCancelamentoService } from 'services/pvf-config-tipos-cancelamento.service';
import { baseDatasourceFactory } from './base.datasource.factory';

export class PvfConfigTiposCancelamentoDataSource extends baseDatasourceFactory(
    pvfConfigTiposCancelamentoService
) {}
