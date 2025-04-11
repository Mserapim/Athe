Ext._define('edocs.protocolo.requestform.blooddonationdayoff.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.blooddonationdayoff.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.blooddonationdayoff.Restful',
    'edocs.protocolo.requestform.blooddonationdayoff.Grid'
);
