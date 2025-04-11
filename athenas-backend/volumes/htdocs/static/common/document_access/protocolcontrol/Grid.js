Ext._define('common.document_access.protocolcontrol.Grid', {
    extend: 'common.document_access.control.Grid',
    restWindow: 'common.document_access.protocolcontrol.Window',
});

core.RestfulGrid.register(
    'common.document_access.protocolcontrol.Restful',
    'common.document_access.protocolcontrol.Grid'
);
