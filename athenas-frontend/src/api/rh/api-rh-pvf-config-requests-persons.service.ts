import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    name?: string;
    cpf?: string;
    rg?: string;
    rg_orgao?: string;
    rg_uf?: number;
    rg_data_expedicao?: Date;
    data_nascimento?: Date | string;
    municipio_naturalidade?: number;
    sexo?: 'M' | 'F';
    sexual_orientation?: number;
    immigrant_residence_time?: number;
    immigrant_entry_condition?: number;
}

export class ApiRhPvfConfigRequestsTypeResponse {
    pk: number;
    name: string;
    cpf: string;
    rg: string;
    rg_orgao: string;
    rg_uf: number;
    rg_data_expedicao: Date;
    data_nascimento: Date;
    municipio_naturalidade: number;
    sexo: 'M' | 'F';
    sexual_orientation: number;
    immigrant_residence_time: number;
    immigrant_entry_condition: number;
}

export async function apiRhPvfConfigRequestsPersons(payload: Payload) {
    return await usePost<ApiRhPvfConfigRequestsTypeResponse>(
        '/rh/pvf/config/requests/persons/',
        payload
    );
}
