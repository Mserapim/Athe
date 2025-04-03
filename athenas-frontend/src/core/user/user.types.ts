export interface User {
    // id: string;
    // name: string;
    email: string;
    avatar?: string;
    status?: string;
    name: string;
    id: number;
    matricula: number;
    workplace: string;
    jobposition: string;
    user: string;
    type_by_possession: string;
    sexo: 'M' | 'F';
    photo: string; //base64
    substitutable: 'NO_REQUIRED' | 'OPTIONAL' | 'REQUIRED';
}
