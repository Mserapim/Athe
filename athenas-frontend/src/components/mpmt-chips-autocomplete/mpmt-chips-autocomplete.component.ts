import {Component, ElementRef, EventEmitter, inject, Input, Output, ViewChild} from '@angular/core';
import {map, Observable, startWith} from "rxjs";
import {FormControl} from "@angular/forms";
import {MatAutocomplete, MatAutocompleteSelectedEvent} from "@angular/material/autocomplete";
import {MatChipInputEvent} from "@angular/material/chips";
import {COMMA, ENTER} from "@angular/cdk/keycodes";
import {SelectItem} from "../../utils/select-item";

@Component({
    selector: 'mpmt-chips-autocomplete',
    templateUrl: './mpmt-chips-autocomplete.component.html',
    styleUrls: ['./mpmt-chips-autocomplete.component.scss'],
    standalone: false
})
export class MpmtChipsAutocompleteComponent {
    separatorKeysCodes: number[] = [ENTER, COMMA];
    @Input() _options: SelectItem[] = [];
    @Input()
    set options(options: SelectItem[]){
        this._options = options;
        this.removerOpcoesSelecionadas();
    }
    @Input() title: string = '';
    @Input() placeholder: string = 'Digite para pesquisar';
    @Output() optionsSelected = new EventEmitter<string []>();
    @Output() filter = new EventEmitter<string>();

    formControl = new FormControl();
    @Input() _selectedOptions: SelectItem[] = [];
    @Input()
    set selectedOptions(selectedOptions: SelectItem[]) {
        this._selectedOptions = selectedOptions;
        this.removerOpcoesSelecionadas();
    }
    textoPesquisa: string;
    inputFocused = false;

    @ViewChild('auto') auto: MatAutocomplete;  // Referência para o mat-autocomplete


    constructor() {
        this._options
    }

    removerOpcoesSelecionadas() {
        if (!this._options)
            return;
        if (!this._selectedOptions)
            return;

        this._options = this._options.filter(option =>
            this._selectedOptions.filter(selectedOption => option.value === selectedOption.value).length == 0)
    }

    add(event: MatChipInputEvent): void {

    }

    onOptionSelected(event: MatAutocompleteSelectedEvent, input: HTMLInputElement): void {
        const selectedOption = this._options.find((option) => option.label === event.option.viewValue);

        if (this._selectedOptions.find(item => selectedOption.value === item.value))
            return;

        this._selectedOptions.push(selectedOption);
        this.optionsSelected.emit(this._selectedOptions.map(option => option.value));

        this.formControl.setValue('');
        this.removerOpcoesSelecionadas()

        setTimeout(() => {
            input.click();  // Força o click para reabrir o painel
        });
    }

    removeOption(optionToRemove: SelectItem): void {
        const indexToRemove = this._selectedOptions.findIndex(
            (selectedOption) => selectedOption.value === optionToRemove.value
        );

        if (indexToRemove !== -1) {
            this._selectedOptions.splice(indexToRemove, 1);
            this.optionsSelected.emit(this._selectedOptions.map(option => option.value));
        }

        this.onInputChange();
    }

    onInputChange(): void {
        this.filter.emit(this.textoPesquisa);
    }

    onFocus() {
        this.inputFocused = true;
    }

    onBlur(event: FocusEvent) {
        const target = event.relatedTarget as HTMLElement;
        if (!target || !target.closest('.chips-container')) {
            this.inputFocused = false;
        }
    }

    removeAll() {
        this._selectedOptions = [];
    }
}
