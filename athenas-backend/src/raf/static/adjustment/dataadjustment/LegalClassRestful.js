Ext._define('raf.LegalClassRestful', {
    extend: 'judicial.taxonomy.LegalClassRestful',

    resource: 'RAFLegalClass',

    // getFields: function(cfg) {
    //     if(!this._fields)
    //         this._fields = raf.LegalClassRestful.superclass.getFields.call(this, cfg).concat([
    //             { },
    //             // { type: 'string', name: 'first_adjustment_date', },
    //         ]);
    //
    //     return this._fields;
    // }

});
