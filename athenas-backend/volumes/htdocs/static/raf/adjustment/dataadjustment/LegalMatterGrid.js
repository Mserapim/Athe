Ext._define('raf.LegalMatterGrid', {
    extend: 'judicial.taxonomy.LegalMatterGrid',

    rest: 'raf.LegalMatterRestful',

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
    'raf.LegalMatterRestful',
    'raf.LegalMatterGrid'
);
