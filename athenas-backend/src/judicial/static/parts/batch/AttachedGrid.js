Ext._define('judicial.parts.batch.AttachedGrid', {
    extend: 'judicial.parts.AttachedGrid',

    restWindow: 'judicial.parts.batch.AttachedWindow',

    actionColumnWidth: 85,

});

core.RestfulGrid.register(
    'judicial.parts.batch.AttachedGrid'
);
