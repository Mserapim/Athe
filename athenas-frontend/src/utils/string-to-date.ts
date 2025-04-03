export const stringToDate = (dataString: string): Date =>{
    const partes = dataString.split('-');
    const ano = parseInt(partes[0], 10);
    const mes = parseInt(partes[1], 10) - 1;
    const dia = parseInt(partes[2], 10);
    const data = new Date(ano, mes, dia);
    return data
}