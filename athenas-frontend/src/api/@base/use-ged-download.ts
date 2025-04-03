import {environment} from 'environments/environment';
import {useGet} from "./use-get";

const API_URL = environment.api_endpoint || 'http://localhost:1231';
const url = (target: string) => {
    if (target.charAt(0) == '/') target = target.substring(1, 10000);
    return `${API_URL}/${target}`;
};

export async function useGedDownload<T>(file_id: string) {
    try {
        const link = url('/ged/download/?file_id=' + file_id);
        // window.open(link, '_blank');

        // const link = url('/report/download/?uuid=' + uuid);
        // window.open(link, '_blank');

        const a = document.createElement('a');
        a.href = link;
        // link.setAttribute('download', title);
        document.body.appendChild(a);
        a.click();
        return;
    } catch (e) {
        alert(e);
    }

    return;
}

export async function useGedUrl<T>(file_id: string) {
    try {
        const link = url('/ged/download/?file_id=' + file_id);
        const response = await useGet(
            `${link}&download=false`,
            {},
            {},
            'arraybuffer'
        );

        const contentType = response.headers['content-type'] as string;
        const blob = new Blob([response.data], { type: contentType });
        return URL.createObjectURL(blob);
    } catch (e) {
        alert(e);
    }

    return;
}

