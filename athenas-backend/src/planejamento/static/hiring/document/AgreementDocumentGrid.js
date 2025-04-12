Ext._define('planning.hiring.document.AgreementDocumentGrid', {
    extend: 'planning.hiring.document.DocumentGrid',
    restWindow: 'planning.hiring.document.AgreementDocumentWindow',
});

core.RestfulGrid.register(
    'planning.hiring.document.AgreementDocumentRestful',
    'planning.hiring.document.AgreementDocumentGrid'
);