Ext._define('raf.LegalMatterRestful', {
    extend: 'judicial.taxonomy.LegalMatterRestful',

    resource: 'RAFLegalMatter',

    // getFields: function(cfg) {
    //     if(!this._fields)
    //         this._fields = raf.LegalMatterRestful.superclass.getFields.call(this, cfg).concat([
    //             { },
    //             // { type: 'string', name: 'first_adjustment_date', },
    //         ]);
    //
    //     return this._fields;
    // }

});
