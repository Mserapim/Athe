Ext._define('edocs.protocolo.requestform.electorallicense.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.electorallicense.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.electorallicense.Restful',
    'edocs.protocolo.requestform.electorallicense.Grid'
);
