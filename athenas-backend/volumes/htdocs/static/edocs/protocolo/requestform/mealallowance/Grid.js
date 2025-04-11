Ext._define('edocs.protocolo.requestform.mealallowance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.mealallowance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.mealallowance.Restful',
    'edocs.protocolo.requestform.mealallowance.Grid'
);
