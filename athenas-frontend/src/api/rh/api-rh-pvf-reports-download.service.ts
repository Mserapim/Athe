import { useGet } from 'api/@base/use-get';

interface Payload {
    uuid?: string;
}

class Response {}

export async function apiRhPvfReportsDownload(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/reports/download/',
        payload
    );
    return data;
}
