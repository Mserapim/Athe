import {
    Component,
    Input,
    OnChanges,
    OnInit,
    ViewEncapsulation,
    forwardRef,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import {
    Alignment,
    Autoformat,
    BlockQuote,
    Bold,
    ClassicEditor,
    CloudServices,
    Essentials,
    Heading,
    ImageCaption,
    ImageStyle,
    ImageToolbar,
    ImageUpload,
    Indent,
    Italic,
    Link,
    List,
    MediaEmbed,
    Mention,
    Paragraph,
    PasteFromOffice,
    Table,
    TableToolbar,
    TextTransformation,
    Undo,
} from 'ckeditor5';
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: 'mpmt-texto-formatado',
    templateUrl: './mpmt-texto-formatado.component.html',
    styleUrls: ['./mpmt-texto-formatado.component.scss'],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MpmtTextoFormatadoComponent),
            multi: true,
        },
    ],
    standalone: false
})
export class MpmtTextoFormatadoComponent
    implements OnInit, OnChanges, ControlValueAccessor
{
    @Input() disabled?: boolean = false;
    @Input() titulo?: string = '';
    @Input() titulo_class?: string = 'text-color';
    @Input() placeholder?: string = '';

    public Editor = ClassicEditor;
    public config = {
        toolbar: [
            'alignment', // Displaying the proper UI element in the toolbar.
            // '|',
            // 'heading',
            '|',
            'bold',
            'italic',
            'link',
            'bulletedList',
            'numberedList',
            '|',
            'outdent',
            'indent',
            '|',
            // 'imageUpload',
            'blockQuote',
            'insertTable',
            // 'mediaEmbed',
            '|',
            'undo',
            'redo',
        ],
        language: 'pt-br',
        image: {
            toolbar: [
                'imageTextAlternative',
                'toggleImageCaption',
                'imageStyle:inline',
                'imageStyle:block',
                'imageStyle:side',
            ],
        },
        table: {
            contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells'],
        },
        plugins: [
            Bold,
            Essentials,
            Italic,
            Mention,
            Paragraph,
            Undo,
            Alignment, // Adding the package to the list of plugins.
            Autoformat,
            BlockQuote,
            // CloudServices,
            Heading,
            Image,
            ImageCaption,
            ImageStyle,
            ImageToolbar,
            ImageUpload,
            Indent,
            Link,
            List,
            // MediaEmbed,
            PasteFromOffice,
            Table,
            TableToolbar,
            TextTransformation,
        ],
    };

    private loadingSubject = new BehaviorSubject<boolean>(false);
    public loading$ = this.loadingSubject.asObservable();

    constructor() {}

    ngOnInit() {}

    ngOnDestroy() {}

    ngOnChanges(changes) {}

    ngAfterViewInit() {}

    updateText($event) {
        const text = $event?.editor?.getData();
        this.onChange(text);
    }

    /** */
    valor: string | number | boolean | object = '';
    onChange: any = () => {};
    onTouched: any = () => {};

    writeValue(value: string | any): void {
        this.valor = value || '';
        this.onChange(this.valor);
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }
    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        setTimeout(() => {
            this.disabled = isDisabled;
        }, 10);
    }
}
