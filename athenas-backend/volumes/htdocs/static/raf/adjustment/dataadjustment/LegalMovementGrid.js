Ext._define('raf.LegalMovementGrid', {
    extend: 'judicial.taxonomy.LegalMovimentGrid',

    rest: 'raf.LegalMovementRestful',

    // getColumnModel: function() {
    //     if(!this._columnModel)
    //         this._columnModel = new Ext.grid.ColumnModel({
    //             columns: [
    //
    //             ],
    //         });
    //     return this._columnModel;
    // },


});

core.RestfulGrid.register(
    'raf.LegalMovementRestful',
    'raf.LegalMovementGrid'
);
