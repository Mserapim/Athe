Ext._define('planning.hiring.document.ValueDocumentGrid', {
    extend: 'planning.hiring.document.DocumentGrid',
    restWindow: 'planning.hiring.document.ValueDocumentWindow',
});

core.RestfulGrid.register(
    'planning.hiring.document.ValueDocumentRestful',
    'planning.hiring.document.ValueDocumentGrid'
);