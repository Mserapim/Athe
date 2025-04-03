import { Moment } from 'moment';

export const formatDate = (date: Date | Moment): string => {
    return date ? date.toISOString().split('T')[0] : '';
};
