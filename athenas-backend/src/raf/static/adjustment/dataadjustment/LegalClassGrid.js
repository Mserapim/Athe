Ext._define('raf.LegalClassGrid', {
    extend: 'judicial.taxonomy.LegalClassGrid',

    rest: 'raf.LegalClassRestful',

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
    'raf.LegalClassRestful',
    'raf.LegalClassGrid'
);
