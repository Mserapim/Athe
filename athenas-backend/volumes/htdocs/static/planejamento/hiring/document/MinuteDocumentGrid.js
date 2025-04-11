Ext._define('planning.hiring.document.MinuteDocumentGrid', {
    extend: 'planning.hiring.document.DocumentGrid',
    restWindow: 'planning.hiring.document.MinuteDocumentWindow',
});

core.RestfulGrid.register(
    'planning.hiring.document.MinuteDocumentRestful',
    'planning.hiring.document.MinuteDocumentGrid'
);