Ext._define('raf.LegalMovementRestful', {
    extend: 'judicial.taxonomy.LegalMovimentRestful',

    resource: 'RAFLegalMovement',

    // getFields: function(cfg) {
    //     if(!this._fields)
    //         this._fields = raf.LegalMovementRestful.superclass.getFields.call(this, cfg).concat([
    //             { },
    //             // { type: 'string', name: 'first_adjustment_date', },
    //         ]);
    //
    //     return this._fields;
    // }

});
