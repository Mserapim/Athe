import { baseDatasourceFactory } from './base.datasource.factory';
import {pvfConfigParamsTypeDependentsService} from "../services/pvf-config-params-type-dependents.service";

export class pvfConfigParamsTypeDependentsDataSource extends baseDatasourceFactory(
    pvfConfigParamsTypeDependentsService
) {}
