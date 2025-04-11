Ext._define('common.document_access.controltype.byUser.Grid', {
    extend: 'common.document_access.controltype.Grid',
    restWindow: 'common.document_access.controltype.byUser.Window',
});

core.RestfulGrid.register(
    'common.document_access.controltype.byUser.Restful',
    'common.document_access.controltype.byUser.Grid'
);
