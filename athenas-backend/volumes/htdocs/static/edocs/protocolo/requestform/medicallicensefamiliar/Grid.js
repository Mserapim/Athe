Ext._define('edocs.protocolo.requestform.medicallicensefamiliar.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.medicallicensefamiliar.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.medicallicensefamiliar.Restful',
    'edocs.protocolo.requestform.medicallicensefamiliar.Grid'
);
