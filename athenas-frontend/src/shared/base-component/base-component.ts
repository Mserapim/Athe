import { Component, OnDestroy } from "@angular/core";
import { Subject } from "rxjs";

@Component({
    selector: 'app-base-component',
    template: `<div>base works!!</div>`,
    standalone: false
})
export class BaseComponent implements OnDestroy {
    /**
    * OPÇÃO 1:
    * subscription com a função de evitar memory leak na aplicação.
    * Manualmente destruimos a assinatura quando o componente for destruído.
    * Mais informações: https://blog.angularindepth.com/the-best-way-to-unsubscribe-rxjs-observable-in-the-angular-applications-d8f9aa42f6a0
    *
    * Implementação:
    * private subscription: Subscription;  // Opção 1
    * 
    * this.subscription = this.loadingService.consultarValorLoading().subscribe((state: LoadingState) => {
    *   this.loading = state.loading;
    * });

    * ngOnDestroy() {
    *   this.subscription.unsubscribe();
    * }
    */

    /**
     * OPÇÃO 2:
     * Gerenciará sua assinatura com base na vida útil do elemento DOM ao qual está associado.
     * O canal assíncrono fará uma nova assinatura onde quer que seja declarado.
     * Use "as" para reutilizar o valor fornecido.
     * 
     * Implementação:
     * <div *ngIf="observable$ | async as data">
     *   {{ data }}
     * </div>
     */

    /**
     * OPÇÃO 3:
     * take, takeUntil e takeWhile gerenciarão uma assinatura automaticamente com base nas condições atendidas.
     * Por exemplo, takeUntil utilizará um observável como argumento e manterá uma assinatura até que esse observável emita um valor.
     * Mais informações: https://itnext.io/angular-rxjs-detecting-memory-leaks-bdd312a070a0
     *                   https://medium.com/@maciekprzybylski/remember-to-unsubscribe-from-streams-in-your-angular-components-caf0bedd6ac2
     * Leitura complementar: https://blog.angulartraining.com/how-to-automatically-unsubscribe-your-rxjs-observables-tutorial-2f98b0560298
     * principalmente a parte dos porquês.
     */
    unsubscribe: Subject<void> = new Subject<void>();

    /**
     * Cancela as assinaturas (observables) para garantir que não haja
     * vazamentos de memória - (Memory Leaks).
     * Cancela a inscrição de todas as subscrições.
     */
    ngOnDestroy(): void {
        this.unsubscribe.next();
        this.unsubscribe.complete();
    }
}