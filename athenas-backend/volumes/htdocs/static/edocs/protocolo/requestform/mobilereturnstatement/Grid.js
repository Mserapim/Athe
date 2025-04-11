Ext._define('edocs.protocolo.requestform.mobilereturnstatement.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.mobilereturnstatement.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.mobilereturnstatement.Restful',
    'edocs.protocolo.requestform.mobilereturnstatement.Grid'
);
