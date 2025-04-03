import { usePost } from 'api/@base/use-post';

interface Payload {
    start_date: Date;
    end_date: Date;
    dependent: number;
    birth_certificate: number;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
    criar_solicitacao_creche_ir: boolean;
}

export async function apiRhPvfRequestsAbsencesMaternityAbsencesService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/absences/maternity-absences/',
        payload
    );
    return data;
}
