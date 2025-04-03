import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    usufructs_in: {
        start_date: Date;
        end_date: Date;
        days: number;
        sale_usufruct: number;
    }[];
    type_usufruct: number;
    substitutes: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    parcel_number: number;
    observation: string;
}

class ResponseItem {
    pk: number;
    type_of_request: string;
    date: string;
    employee_name: string;
    approver_name: string;
    status_name: string;
    get_parcel_number: string;
    acquisitive_period: string;
}

class Response extends ResponseItem {}

export function pvfUsufructsRegularVacations(payload: Payload) {
    return usePost<Response>('/rh/pvf/usufructs/regular_vacations', payload);
}
