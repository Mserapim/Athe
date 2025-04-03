export const addMinute = (date: Date, n: number): Date => {
    const d = new Date();
    d.setTime(d.getTime() + n * 60 * 1000);
    return d;
};
