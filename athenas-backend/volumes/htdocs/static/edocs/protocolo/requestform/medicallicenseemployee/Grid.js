Ext._define('edocs.protocolo.requestform.medicallicenseemployee.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.medicallicenseemployee.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.medicallicenseemployee.Restful',
    'edocs.protocolo.requestform.medicallicenseemployee.Grid'
);
