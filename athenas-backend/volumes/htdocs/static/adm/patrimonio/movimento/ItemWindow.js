/**
 *
 **/
Ext._define('adm.patrimonio.movimento.ItemWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.movimento.ItemRestful',

    width: 650,

    // getFormPanel: function() {
    //     if(!this._formPanel)
    //         this._formPanel = Ext._create('Ext.form.FormPanel', {
    //             border: false,
    //             frame: false,
    //             layout: 'fit',
    //             items: [
    //                 Ext._create('toolkit.fields.CKEditor', {
    //                     name: 'comentario',
    //                     height: 300
    //                 })
    //             ]
    //         });

    //     return this._formPanel;
    // }
});
