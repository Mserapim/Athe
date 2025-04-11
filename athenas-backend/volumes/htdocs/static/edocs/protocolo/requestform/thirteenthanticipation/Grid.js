Ext._define('edocs.protocolo.requestform.thirteenthanticipation.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.thirteenthanticipation.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.thirteenthanticipation.Restful',
    'edocs.protocolo.requestform.thirteenthanticipation.Grid'
);
