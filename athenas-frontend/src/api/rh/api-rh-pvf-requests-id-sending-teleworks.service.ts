import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    targets: {
        id: number;
        total_completed: number;
        mark_situation: number;
        observation: string; //Será removido
    }[];
    observation: string;
    anexo_id:number;
}

class Response {}

export async function apiRhPvfRequestsIdSendingTeleworksService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        `rh/pvf/requests/${payload.id}/sending-teleworks/`,
        payload
    );
    return data;
}
