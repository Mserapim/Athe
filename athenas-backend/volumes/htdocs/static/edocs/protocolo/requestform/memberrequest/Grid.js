Ext._define('edocs.protocolo.requestform.memberrequest.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.memberrequest.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.memberrequest.Restful',
    'edocs.protocolo.requestform.memberrequest.Grid'
);
