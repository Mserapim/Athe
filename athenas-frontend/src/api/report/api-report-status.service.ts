import { useGet } from 'api/@base/use-get';

interface Payload {
    uuid?: string;
}

class Response {
    status: 'processing' | 'success' | string;
}

export async function apiReportStatus(payload: Payload) {
    const { data } = await useGet<Response>('report/status/', payload);
    return data;
}
