export const printDate = (date: Date | string): string => {
    if (!date) return '';
    let str: string;
    if (typeof date == 'object') str = new Date(date).toISOString();
    else str = date;

    str = str.substring(0, 12);
    const strSplited = str.split('-');

    return strSplited[2] + '/' + strSplited[1] + '/' + strSplited[0];
};
