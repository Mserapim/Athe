Ext._define('edocs.protocolo.requestform.employeerequest.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.employeerequest.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.employeerequest.Restful',
    'edocs.protocolo.requestform.employeerequest.Grid'
);
