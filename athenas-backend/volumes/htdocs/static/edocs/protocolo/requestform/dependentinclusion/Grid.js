Ext._define('edocs.protocolo.requestform.dependentinclusion.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.dependentinclusion.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.dependentinclusion.Restful',
    'edocs.protocolo.requestform.dependentinclusion.Grid'
);
