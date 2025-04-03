import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    fileName: string;
    file: File;
    format_valid?:string;
}

class GedUploadResponse {
    file_id: number;
    message: string;
    success: boolean;
}

export async function gedUpload2(payload: Payload) {
    let bodyFormData = new FormData();
    bodyFormData.append('file', payload.file);
    bodyFormData.append('name', payload.fileName);
    if(payload.format_valid)
        bodyFormData.append('format_valid',payload.format_valid);
    const response = await usePost<GedUploadResponse>('ged/upload/', bodyFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response?.data;
}
