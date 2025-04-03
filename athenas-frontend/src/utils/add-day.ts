import moment, { Moment } from 'moment';

export const addDay = (date: Date, n: number): Date => {
    // console.log('date', date, date instanceof moment, typeof date);
    if (date instanceof moment) {
        let a = moment(date);
        a = a.add(n, 'days');
        return a.toDate();
    } else {
        const d = new Date();
        d.setTime(date.getTime() + n * 24 * 60 * 60 * 1000);
        return d;
    }
};
