import { AxiosBaseResponse } from './axios-base-response';
import axios from 'axios';
import { environment } from 'environments/environment';

const API_URL = environment.api_endpoint || 'http://localhost:1231';
const url = (target: string) => `${API_URL}/${target}`;

export const useDelete = async <M extends object | [] = any>(
    target: string,
    payload: any = {},
    headers: any = {}
): Promise<AxiosBaseResponse<M>> => {
    return await axios
        .delete(url(target), {
            headers: { ...headers, remote: environment.remote },
            params: payload,
        })
        .catch((error) => {
            throw new AxiosBaseResponse<M>(error);
        })
        .then((response) => {
            return new AxiosBaseResponse<M>(response);
        });
};
