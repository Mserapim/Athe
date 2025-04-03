import { Component, EventEmitter, Input, Output } from '@angular/core';
import {FormBuilder, FormGroup} from "@angular/forms";
import {
    apiPainelControleControleAcessoIcons
} from "../../api/painel-controle/api-painel-controle-controle-acesso-icons.service";
import {map, Observable, startWith} from "rxjs";

@Component({
    selector: 'mpmt-selecao-icones',
    templateUrl: './mpmt-selecao-icones.component.html',
    styleUrls: ['./mpmt-selecao-icones.component.scss'],
    standalone: false
})
export class MpmtSelecaoIconesComponent {
    @Input() _selectedIcon: string = '';
    @Output() iconSelected = new EventEmitter<string>();

    icons: string[] = [];

    form: FormGroup;

    filteredIcons: Observable<string[]>;

    @Input()
    titulo: string = 'Ícone*'

    @Input()
    set selectedIcon(value: string) {
        this._selectedIcon = value;
        this.form.get('selectedIcon').setValue(this._selectedIcon);
    }

    ngOnInit(): void {
        apiPainelControleControleAcessoIcons(null).then(response => {
            this.icons.push(...response.results);

            this.filteredIcons = this.form.get('selectedIcon').valueChanges.pipe(
                startWith(''),
                map(value => this._filterIcons(value))
            );
        });
    }

    displayFn(icon: string): string {
        return icon || '';
    }

    constructor(private formBuilder: FormBuilder) {
        this.form = this.formBuilder.group({
            selectedIcon: [this.selectedIcon ? this.selectedIcon : '']
        });
        this.form.get('selectedIcon')!.valueChanges.subscribe((value: string) => {
            this.iconSelected.emit(value);
        });
    }

    private _filterIcons(value: string): string[] {
        const filterValue = value.toLowerCase();
        return this.icons.filter(icon => icon.toLowerCase().includes(filterValue));
    }
}
