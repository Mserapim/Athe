Ext._define('edocs.protocolo.requestform.removenotificationresistance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.removenotificationresistance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.removenotificationresistance.Restful',
    'edocs.protocolo.requestform.removenotificationresistance.Grid'
);
