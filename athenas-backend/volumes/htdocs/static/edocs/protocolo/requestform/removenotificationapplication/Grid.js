Ext._define('edocs.protocolo.requestform.removenotificationapplication.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.removenotificationapplication.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.removenotificationapplication.Restful',
    'edocs.protocolo.requestform.removenotificationapplication.Grid'
);
