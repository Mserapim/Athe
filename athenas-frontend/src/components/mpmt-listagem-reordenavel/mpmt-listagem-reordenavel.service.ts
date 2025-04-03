import { MpmtListagem2Linha } from "components/mpmt-listagem2/mpmt-listagem2.interface";
import { MpmtListagem2Service } from "components/mpmt-listagem2/mpmt-listagem2.service";

export abstract class MpmtListagemReordenavelService<T extends any = any> extends MpmtListagem2Service<T> {
    constructor() {
        super();
    }

    public async atualizarOrdem(dados: MpmtListagem2Linha[]): Promise<any> {
        throw new Error("Este método deve ser implementado pela subclasse.");
    }

}