Ext._define('edocs.protocolo.requestform.childbirthdayoff.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.childbirthdayoff.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.childbirthdayoff.Restful',
    'edocs.protocolo.requestform.childbirthdayoff.Grid'
);
