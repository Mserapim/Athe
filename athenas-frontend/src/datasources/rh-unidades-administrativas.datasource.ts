import { baseDatasourceFactory } from './base.datasource.factory';
import {apiRhUnidadesAdministrativas} from "../api/rh/api-rh-unidades-administrativas.service";

export class RhUnidadesAdministrativasDatasource extends baseDatasourceFactory(
    apiRhUnidadesAdministrativas
) {}
