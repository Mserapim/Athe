import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { useGedDownload } from 'api/@base/use-ged-download';

export interface Documento {
  id: number;
  description: string;
  name: string;
  attachment_id: number;
  originalName: string;
}

@Component({
    selector: 'mpmt-file-update',
    templateUrl: './mpmt-file-update.component.html',
    styleUrls: ['./mpmt-file-update.component.scss'],
    standalone: false
})
export class MpmtFileUpdateComponent implements OnInit, OnChanges {
  @Input() acceptMultiple: boolean = false;
  @Input() acceptedFileTypes: string[] = [];
  @Input() lista_arquivos_carregados: Documento[] = [];
  @Input() titulo: string = 'Adicionar documentos';
  @Input() isReadOnly: boolean = false; // Novo Input para estado de leitura
  @Output() lista_documentos = new EventEmitter<number[]>();

  documentos: Documento[] = [];

  constructor(
    protected snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    this.initializeDocumentos();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.lista_arquivos_carregados) {
      this.initializeDocumentos();
    }
  }

  initializeDocumentos() {
    if (this.lista_arquivos_carregados && this.lista_arquivos_carregados.length > 0) {
      this.documentos = [...this.lista_arquivos_carregados];
      this.emitChanges();
    }
  }

  async onFileInput(event: any) {
    if (this.isReadOnly) return;
    if (this.validarMultiplo()) return;
    const files: FileList = event.target.files;
    if (files.length > 0) {
      await this.handleFiles(files);
    }
  }

  onDragOver(event: any) {
    if (this.isReadOnly) return;
    event.preventDefault();
  }

  onDrop(event: any) {
    if (this.isReadOnly) return;
    if (this.validarMultiplo()) return;
    event.preventDefault();
    const files: FileList = event.dataTransfer.files;
    this.handleFiles(files);
  }

  onDragStart(event: any, id: string) {
    if (this.isReadOnly) return;
    if (this.validarMultiplo()) return;
    event.dataTransfer.setData('text/plain', id);
  }

  async handleFiles(files: FileList) {
    if (this.isReadOnly) return;
    if (this.validarMultiplo()) return;
    for (let i = 0; i < files.length; i++) {
      const file: File = files[i];
      if (this.isFileTypeAccepted(file)) {
        try {
          const response = await gedUpload({
            file: file,
            fileName: file.name,
          });

          const newDocumento: Documento = {
            id: new Date().getTime(), // Assuming you generate IDs as timestamps
            description: '',
            name: file.name,
            attachment_id: response.data.file_id,
            originalName: file.name,
          };

          this.documentos.push(newDocumento);
        } catch (error) {
          console.error('Erro no upload do arquivo:', error);
          this.exibirMensagem('Erro', 'Falha ao fazer o upload do arquivo.');
        }
      } else {
        console.log(`Tipo de arquivo ${file.type} não é aceito.`);
        this.exibirMensagem('Atenção', `Tipo de arquivo ${file.type} não é aceito.`);
      }
    }
    this.emitChanges();
  }

  removeItem(id: number) {
    if (this.isReadOnly) return;
    this.documentos = this.documentos.filter((x) => x.id !== id);
    this.emitChanges();
  }

  private isFileTypeAccepted(file: File): boolean {
    if (this.acceptedFileTypes.length === 0) return true;
    return this.acceptedFileTypes.includes(file.type);
  }

  getDocumentos(): Documento[] {
    return this.documentos;
  }

  private emitChanges() {
    this.lista_documentos.emit(this.documentos.map(item => item.attachment_id));
  }

  protected exibirMensagem(titulo: string, texto: string) {
    this.snackBar.open(texto, '', {
      duration: 4000,
      horizontalPosition: 'center',
      verticalPosition: 'top',
      panelClass: ['custom-snackbar']
    });
  }

  validarMultiplo(): boolean {
      if (!this.acceptMultiple && this.documentos.length > 0) return;
  }

  public async downloadArquivo(id){
    useGedDownload(id);
  }

}
